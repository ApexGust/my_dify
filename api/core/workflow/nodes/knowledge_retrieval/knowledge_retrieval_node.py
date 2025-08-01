import json
import logging
import re
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Optional, cast

from sqlalchemy import Float, and_, func, or_, text
from sqlalchemy import cast as sqlalchemy_cast
from sqlalchemy.orm import Session

from core.app.app_config.entities import DatasetRetrieveConfigEntity
from core.app.entities.app_invoke_entities import ModelConfigWithCredentialsEntity
from core.entities.agent_entities import PlanningStrategy
from core.entities.model_entities import ModelStatus
from core.model_manager import ModelInstance, ModelManager
from core.model_runtime.entities.message_entities import (
    PromptMessageRole,
)
from core.model_runtime.entities.model_entities import (
    ModelFeature,
    ModelType,
)
from core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel
from core.prompt.simple_prompt_transform import ModelMode
from core.rag.datasource.retrieval_service import RetrievalService
from core.rag.entities.metadata_entities import Condition, MetadataCondition
from core.rag.retrieval.dataset_retrieval import DatasetRetrieval
from core.rag.retrieval.retrieval_methods import RetrievalMethod
from core.variables import (
    StringSegment,
)
from core.variables.segments import ArrayObjectSegment
from core.workflow.entities.node_entities import NodeRunResult
from core.workflow.entities.workflow_node_execution import WorkflowNodeExecutionStatus
from core.workflow.nodes.base import BaseNode
from core.workflow.nodes.base.entities import BaseNodeData, RetryConfig
from core.workflow.nodes.enums import ErrorStrategy, NodeType
from core.workflow.nodes.event import (
    ModelInvokeCompletedEvent,
)
from core.workflow.nodes.knowledge_retrieval.template_prompts import (
    METADATA_FILTER_ASSISTANT_PROMPT_1,
    METADATA_FILTER_ASSISTANT_PROMPT_2,
    METADATA_FILTER_COMPLETION_PROMPT,
    METADATA_FILTER_SYSTEM_PROMPT,
    METADATA_FILTER_USER_PROMPT_1,
    METADATA_FILTER_USER_PROMPT_2,
    METADATA_FILTER_USER_PROMPT_3,
)
from core.workflow.nodes.llm.entities import LLMNodeChatModelMessage, LLMNodeCompletionModelPromptTemplate, ModelConfig
from core.workflow.nodes.llm.file_saver import FileSaverImpl, LLMFileSaver
from core.workflow.nodes.llm.node import LLMNode
from extensions.ext_database import db
from extensions.ext_redis import redis_client
from libs.json_in_md_parser import parse_and_check_json_markdown
from models.dataset import Dataset, DatasetMetadata, Document, RateLimitLog
from services.feature_service import FeatureService

from .entities import KnowledgeRetrievalNodeData
from .exc import (
    InvalidModelTypeError,
    KnowledgeRetrievalNodeError,
    ModelCredentialsNotInitializedError,
    ModelNotExistError,
    ModelNotSupportedError,
    ModelQuotaExceededError,
)

if TYPE_CHECKING:
    from core.file.models import File
    from core.workflow.graph_engine import Graph, GraphInitParams, GraphRuntimeState

logger = logging.getLogger(__name__)

default_retrieval_model = {
    "search_method": RetrievalMethod.SEMANTIC_SEARCH.value,
    "reranking_enable": False,
    "reranking_model": {"reranking_provider_name": "", "reranking_model_name": ""},
    "top_k": 2,
    "score_threshold_enabled": False,
}


class KnowledgeRetrievalNode(BaseNode):
    _node_type = NodeType.KNOWLEDGE_RETRIEVAL

    _node_data: KnowledgeRetrievalNodeData

    # Instance attributes specific to LLMNode.
    # Output variable for file
    _file_outputs: list["File"]

    _llm_file_saver: LLMFileSaver

    def __init__(
        self,
        id: str,
        config: Mapping[str, Any],
        graph_init_params: "GraphInitParams",
        graph: "Graph",
        graph_runtime_state: "GraphRuntimeState",
        previous_node_id: Optional[str] = None,
        thread_pool_id: Optional[str] = None,
        *,
        llm_file_saver: LLMFileSaver | None = None,
    ) -> None:
        super().__init__(
            id=id,
            config=config,
            graph_init_params=graph_init_params,
            graph=graph,
            graph_runtime_state=graph_runtime_state,
            previous_node_id=previous_node_id,
            thread_pool_id=thread_pool_id,
        )
        # LLM file outputs, used for MultiModal outputs.
        self._file_outputs: list[File] = []

        if llm_file_saver is None:
            llm_file_saver = FileSaverImpl(
                user_id=graph_init_params.user_id,
                tenant_id=graph_init_params.tenant_id,
            )
        self._llm_file_saver = llm_file_saver

    def init_node_data(self, data: Mapping[str, Any]) -> None:
        self._node_data = KnowledgeRetrievalNodeData.model_validate(data)

    def _get_error_strategy(self) -> Optional[ErrorStrategy]:
        return self._node_data.error_strategy

    def _get_retry_config(self) -> RetryConfig:
        return self._node_data.retry_config

    def _get_title(self) -> str:
        return self._node_data.title

    def _get_description(self) -> Optional[str]:
        return self._node_data.desc

    def _get_default_value_dict(self) -> dict[str, Any]:
        return self._node_data.default_value_dict

    def get_base_node_data(self) -> BaseNodeData:
        return self._node_data

    @classmethod
    def version(cls):
        return "1"

    def _run(self) -> NodeRunResult:  # type: ignore
        # extract variables
        variable = self.graph_runtime_state.variable_pool.get(self._node_data.query_variable_selector)
        if not isinstance(variable, StringSegment):
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs={},
                error="Query variable is not string type.",
            )
        query = variable.value
        variables = {"query": query}
        if not query:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED, inputs=variables, error="Query is required."
            )
        # TODO(-LAN-): Move this check outside.
        # check rate limit
        knowledge_rate_limit = FeatureService.get_knowledge_rate_limit(self.tenant_id)
        if knowledge_rate_limit.enabled:
            current_time = int(time.time() * 1000)
            key = f"rate_limit_{self.tenant_id}"
            redis_client.zadd(key, {current_time: current_time})
            redis_client.zremrangebyscore(key, 0, current_time - 60000)
            request_count = redis_client.zcard(key)
            if request_count > knowledge_rate_limit.limit:
                with Session(db.engine) as session:
                    # add ratelimit record
                    rate_limit_log = RateLimitLog(
                        tenant_id=self.tenant_id,
                        subscription_plan=knowledge_rate_limit.subscription_plan,
                        operation="knowledge",
                    )
                    session.add(rate_limit_log)
                    session.commit()
                return NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs=variables,
                    error="Sorry, you have reached the knowledge base request rate limit of your subscription.",
                    error_type="RateLimitExceeded",
                )

        # retrieve knowledge
        try:
            results = self._fetch_dataset_retriever(node_data=self._node_data, query=query)
            outputs = {"result": ArrayObjectSegment(value=results)}
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs=variables,
                process_data=None,
                outputs=outputs,  # type: ignore
            )

        except KnowledgeRetrievalNodeError as e:
            logger.warning("Error when running knowledge retrieval node")
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs=variables,
                error=str(e),
                error_type=type(e).__name__,
            )
        # Temporary handle all exceptions from DatasetRetrieval class here.
        except Exception as e:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs=variables,
                error=str(e),
                error_type=type(e).__name__,
            )
        finally:
            db.session.close()

    def _fetch_dataset_retriever(self, node_data: KnowledgeRetrievalNodeData, query: str) -> list[dict[str, Any]]:
        available_datasets = []
        dataset_ids = node_data.dataset_ids

        # Subquery: Count the number of available documents for each dataset
        subquery = (
            db.session.query(Document.dataset_id, func.count(Document.id).label("available_document_count"))
            .where(
                Document.indexing_status == "completed",
                Document.enabled == True,
                Document.archived == False,
                Document.dataset_id.in_(dataset_ids),
            )
            .group_by(Document.dataset_id)
            .having(func.count(Document.id) > 0)
            .subquery()
        )

        results = (
            db.session.query(Dataset)
            .outerjoin(subquery, Dataset.id == subquery.c.dataset_id)
            .where(Dataset.tenant_id == self.tenant_id, Dataset.id.in_(dataset_ids))
            .where((subquery.c.available_document_count > 0) | (Dataset.provider == "external"))
            .all()
        )

        # avoid blocking at retrieval
        db.session.close()

        for dataset in results:
            # pass if dataset is not available
            if not dataset:
                continue
            available_datasets.append(dataset)
        metadata_filter_document_ids, metadata_condition = self._get_metadata_filter_condition(
            [dataset.id for dataset in available_datasets], query, node_data
        )
        all_documents = []
        dataset_retrieval = DatasetRetrieval()
        if node_data.retrieval_mode == DatasetRetrieveConfigEntity.RetrieveStrategy.SINGLE.value:
            # fetch model config
            if node_data.single_retrieval_config is None:
                raise ValueError("single_retrieval_config is required")
            model_instance, model_config = self.get_model_config(node_data.single_retrieval_config.model)
            # check model is support tool calling
            model_type_instance = model_config.provider_model_bundle.model_type_instance
            model_type_instance = cast(LargeLanguageModel, model_type_instance)
            # get model schema
            model_schema = model_type_instance.get_model_schema(
                model=model_config.model, credentials=model_config.credentials
            )

            if model_schema:
                planning_strategy = PlanningStrategy.REACT_ROUTER
                features = model_schema.features
                if features:
                    if ModelFeature.TOOL_CALL in features or ModelFeature.MULTI_TOOL_CALL in features:
                        planning_strategy = PlanningStrategy.ROUTER
                all_documents = dataset_retrieval.single_retrieve(
                    available_datasets=available_datasets,
                    tenant_id=self.tenant_id,
                    user_id=self.user_id,
                    app_id=self.app_id,
                    user_from=self.user_from.value,
                    query=query,
                    model_config=model_config,
                    model_instance=model_instance,
                    planning_strategy=planning_strategy,
                    metadata_filter_document_ids=metadata_filter_document_ids,
                    metadata_condition=metadata_condition,
                )
        elif node_data.retrieval_mode == DatasetRetrieveConfigEntity.RetrieveStrategy.MULTIPLE.value:
            if node_data.multiple_retrieval_config is None:
                raise ValueError("multiple_retrieval_config is required")
            if node_data.multiple_retrieval_config.reranking_mode == "reranking_model":
                if node_data.multiple_retrieval_config.reranking_model:
                    reranking_model = {
                        "reranking_provider_name": node_data.multiple_retrieval_config.reranking_model.provider,
                        "reranking_model_name": node_data.multiple_retrieval_config.reranking_model.model,
                    }
                else:
                    reranking_model = None
                weights = None
            elif node_data.multiple_retrieval_config.reranking_mode == "weighted_score":
                if node_data.multiple_retrieval_config.weights is None:
                    raise ValueError("weights is required")
                reranking_model = None
                vector_setting = node_data.multiple_retrieval_config.weights.vector_setting
                weights = {
                    "vector_setting": {
                        "vector_weight": vector_setting.vector_weight,
                        "embedding_provider_name": vector_setting.embedding_provider_name,
                        "embedding_model_name": vector_setting.embedding_model_name,
                    },
                    "keyword_setting": {
                        "keyword_weight": node_data.multiple_retrieval_config.weights.keyword_setting.keyword_weight
                    },
                }
            else:
                reranking_model = None
                weights = None
            all_documents = dataset_retrieval.multiple_retrieve(
                app_id=self.app_id,
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                user_from=self.user_from.value,
                available_datasets=available_datasets,
                query=query,
                top_k=node_data.multiple_retrieval_config.top_k,
                score_threshold=node_data.multiple_retrieval_config.score_threshold
                if node_data.multiple_retrieval_config.score_threshold is not None
                else 0.0,
                reranking_mode=node_data.multiple_retrieval_config.reranking_mode,
                reranking_model=reranking_model,
                weights=weights,
                reranking_enable=node_data.multiple_retrieval_config.reranking_enable,
                metadata_filter_document_ids=metadata_filter_document_ids,
                metadata_condition=metadata_condition,
            )
        dify_documents = [item for item in all_documents if item.provider == "dify"]
        external_documents = [item for item in all_documents if item.provider == "external"]
        retrieval_resource_list = []
        # deal with external documents
        for item in external_documents:
            source = {
                "metadata": {
                    "_source": "knowledge",
                    "dataset_id": item.metadata.get("dataset_id"),
                    "dataset_name": item.metadata.get("dataset_name"),
                    "document_id": item.metadata.get("document_id") or item.metadata.get("title"),
                    "document_name": item.metadata.get("title"),
                    "data_source_type": "external",
                    "retriever_from": "workflow",
                    "score": item.metadata.get("score"),
                    "doc_metadata": item.metadata,
                },
                "title": item.metadata.get("title"),
                "content": item.page_content,
            }
            retrieval_resource_list.append(source)
        # deal with dify documents
        if dify_documents:
            records = RetrievalService.format_retrieval_documents(dify_documents)
            if records:
                for record in records:
                    segment = record.segment
                    dataset = db.session.query(Dataset).filter_by(id=segment.dataset_id).first()  # type: ignore
                    document = (
                        db.session.query(Document)
                        .where(
                            Document.id == segment.document_id,
                            Document.enabled == True,
                            Document.archived == False,
                        )
                        .first()
                    )
                    if dataset and document:
                        source = {
                            "metadata": {
                                "_source": "knowledge",
                                "dataset_id": dataset.id,
                                "dataset_name": dataset.name,
                                "document_id": document.id,
                                "document_name": document.name,
                                "data_source_type": document.data_source_type,
                                "segment_id": segment.id,
                                "retriever_from": "workflow",
                                "score": record.score or 0.0,
                                "segment_hit_count": segment.hit_count,
                                "segment_word_count": segment.word_count,
                                "segment_position": segment.position,
                                "segment_index_node_hash": segment.index_node_hash,
                                "doc_metadata": document.doc_metadata,
                            },
                            "title": document.name,
                        }
                        if segment.answer:
                            source["content"] = f"question:{segment.get_sign_content()} \nanswer:{segment.answer}"
                        else:
                            source["content"] = segment.get_sign_content()
                        retrieval_resource_list.append(source)
        if retrieval_resource_list:
            retrieval_resource_list = sorted(
                retrieval_resource_list,
                key=lambda x: x["metadata"]["score"] if x["metadata"].get("score") is not None else 0.0,
                reverse=True,
            )
            for position, item in enumerate(retrieval_resource_list, start=1):
                item["metadata"]["position"] = position
        return retrieval_resource_list

    def _get_metadata_filter_condition(
        self, dataset_ids: list, query: str, node_data: KnowledgeRetrievalNodeData
    ) -> tuple[Optional[dict[str, list[str]]], Optional[MetadataCondition]]:
        document_query = db.session.query(Document).where(
            Document.dataset_id.in_(dataset_ids),
            Document.indexing_status == "completed",
            Document.enabled == True,
            Document.archived == False,
        )
        filters = []  # type: ignore
        metadata_condition = None
        if node_data.metadata_filtering_mode == "disabled":
            return None, None
        elif node_data.metadata_filtering_mode == "automatic":
            automatic_metadata_filters = self._automatic_metadata_filter_func(dataset_ids, query, node_data)
            if automatic_metadata_filters:
                conditions = []
                for sequence, filter in enumerate(automatic_metadata_filters):
                    self._process_metadata_filter_func(
                        sequence,
                        filter.get("condition", ""),
                        filter.get("metadata_name", ""),
                        filter.get("value"),
                        filters,  # type: ignore
                    )
                    conditions.append(
                        Condition(
                            name=filter.get("metadata_name"),  # type: ignore
                            comparison_operator=filter.get("condition"),  # type: ignore
                            value=filter.get("value"),
                        )
                    )
                metadata_condition = MetadataCondition(
                    logical_operator=node_data.metadata_filtering_conditions.logical_operator
                    if node_data.metadata_filtering_conditions
                    else "or",  # type: ignore
                    conditions=conditions,
                )
        elif node_data.metadata_filtering_mode == "manual":
            if node_data.metadata_filtering_conditions:
                conditions = []
                for sequence, condition in enumerate(node_data.metadata_filtering_conditions.conditions):  # type: ignore
                    metadata_name = condition.name
                    expected_value = condition.value
                    if expected_value is not None and condition.comparison_operator not in ("empty", "not empty"):
                        if isinstance(expected_value, str):
                            expected_value = self.graph_runtime_state.variable_pool.convert_template(
                                expected_value
                            ).value[0]
                            if expected_value.value_type in {"number", "integer", "float"}:  # type: ignore
                                expected_value = expected_value.value  # type: ignore
                            elif expected_value.value_type == "string":  # type: ignore
                                expected_value = re.sub(r"[\r\n\t]+", " ", expected_value.text).strip()  # type: ignore
                            else:
                                raise ValueError("Invalid expected metadata value type")
                    conditions.append(
                        Condition(
                            name=metadata_name,
                            comparison_operator=condition.comparison_operator,
                            value=expected_value,
                        )
                    )
                    filters = self._process_metadata_filter_func(
                        sequence,
                        condition.comparison_operator,
                        metadata_name,
                        expected_value,
                        filters,
                    )
                metadata_condition = MetadataCondition(
                    logical_operator=node_data.metadata_filtering_conditions.logical_operator,
                    conditions=conditions,
                )
        else:
            raise ValueError("Invalid metadata filtering mode")
        if filters:
            if (
                node_data.metadata_filtering_conditions
                and node_data.metadata_filtering_conditions.logical_operator == "and"
            ):  # type: ignore
                document_query = document_query.where(and_(*filters))
            else:
                document_query = document_query.where(or_(*filters))
        documents = document_query.all()
        # group by dataset_id
        metadata_filter_document_ids = defaultdict(list) if documents else None  # type: ignore
        for document in documents:
            metadata_filter_document_ids[document.dataset_id].append(document.id)  # type: ignore
        return metadata_filter_document_ids, metadata_condition

    def _automatic_metadata_filter_func(
        self, dataset_ids: list, query: str, node_data: KnowledgeRetrievalNodeData
    ) -> list[dict[str, Any]]:
        # get all metadata field
        metadata_fields = db.session.query(DatasetMetadata).where(DatasetMetadata.dataset_id.in_(dataset_ids)).all()
        all_metadata_fields = [metadata_field.name for metadata_field in metadata_fields]
        if node_data.metadata_model_config is None:
            raise ValueError("metadata_model_config is required")
        # get metadata model instance and fetch model config
        model_instance, model_config = self.get_model_config(node_data.metadata_model_config)
        # fetch prompt messages
        prompt_template = self._get_prompt_template(
            node_data=node_data,
            metadata_fields=all_metadata_fields,
            query=query or "",
        )
        prompt_messages, stop = LLMNode.fetch_prompt_messages(
            prompt_template=prompt_template,
            sys_query=query,
            memory=None,
            model_config=model_config,
            sys_files=[],
            vision_enabled=node_data.vision.enabled,
            vision_detail=node_data.vision.configs.detail,
            variable_pool=self.graph_runtime_state.variable_pool,
            jinja2_variables=[],
            tenant_id=self.tenant_id,
        )

        result_text = ""
        try:
            # handle invoke result
            generator = LLMNode.invoke_llm(
                node_data_model=node_data.metadata_model_config,
                model_instance=model_instance,
                prompt_messages=prompt_messages,
                stop=stop,
                user_id=self.user_id,
                structured_output_enabled=self._node_data.structured_output_enabled,
                structured_output=None,
                file_saver=self._llm_file_saver,
                file_outputs=self._file_outputs,
                node_id=self.node_id,
            )

            for event in generator:
                if isinstance(event, ModelInvokeCompletedEvent):
                    result_text = event.text
                    break

            result_text_json = parse_and_check_json_markdown(result_text, [])
            automatic_metadata_filters = []
            if "metadata_map" in result_text_json:
                metadata_map = result_text_json["metadata_map"]
                for item in metadata_map:
                    if item.get("metadata_field_name") in all_metadata_fields:
                        automatic_metadata_filters.append(
                            {
                                "metadata_name": item.get("metadata_field_name"),
                                "value": item.get("metadata_field_value"),
                                "condition": item.get("comparison_operator"),
                            }
                        )
        except Exception as e:
            return []
        return automatic_metadata_filters

    def _process_metadata_filter_func(
        self, sequence: int, condition: str, metadata_name: str, value: Optional[Any], filters: list
    ):
        if value is None:
            return

        key = f"{metadata_name}_{sequence}"
        key_value = f"{metadata_name}_{sequence}_value"
        match condition:
            case "contains":
                filters.append(
                    (text(f"documents.doc_metadata ->> :{key} LIKE :{key_value}")).params(
                        **{key: metadata_name, key_value: f"%{value}%"}
                    )
                )
            case "not contains":
                filters.append(
                    (text(f"documents.doc_metadata ->> :{key} NOT LIKE :{key_value}")).params(
                        **{key: metadata_name, key_value: f"%{value}%"}
                    )
                )
            case "start with":
                filters.append(
                    (text(f"documents.doc_metadata ->> :{key} LIKE :{key_value}")).params(
                        **{key: metadata_name, key_value: f"{value}%"}
                    )
                )
            case "end with":
                filters.append(
                    (text(f"documents.doc_metadata ->> :{key} LIKE :{key_value}")).params(
                        **{key: metadata_name, key_value: f"%{value}"}
                    )
                )
            case "=" | "is":
                if isinstance(value, str):
                    filters.append(Document.doc_metadata[metadata_name] == f'"{value}"')
                else:
                    filters.append(sqlalchemy_cast(Document.doc_metadata[metadata_name].astext, Float) == value)
            case "is not" | "≠":
                if isinstance(value, str):
                    filters.append(Document.doc_metadata[metadata_name] != f'"{value}"')
                else:
                    filters.append(sqlalchemy_cast(Document.doc_metadata[metadata_name].astext, Float) != value)
            case "empty":
                filters.append(Document.doc_metadata[metadata_name].is_(None))
            case "not empty":
                filters.append(Document.doc_metadata[metadata_name].isnot(None))
            case "before" | "<":
                filters.append(sqlalchemy_cast(Document.doc_metadata[metadata_name].astext, Float) < value)
            case "after" | ">":
                filters.append(sqlalchemy_cast(Document.doc_metadata[metadata_name].astext, Float) > value)
            case "≤" | "<=":
                filters.append(sqlalchemy_cast(Document.doc_metadata[metadata_name].astext, Float) <= value)
            case "≥" | ">=":
                filters.append(sqlalchemy_cast(Document.doc_metadata[metadata_name].astext, Float) >= value)
            case _:
                pass
        return filters

    @classmethod
    def _extract_variable_selector_to_variable_mapping(
        cls,
        *,
        graph_config: Mapping[str, Any],
        node_id: str,
        node_data: Mapping[str, Any],
    ) -> Mapping[str, Sequence[str]]:
        # Create typed NodeData from dict
        typed_node_data = KnowledgeRetrievalNodeData.model_validate(node_data)

        variable_mapping = {}
        variable_mapping[node_id + ".query"] = typed_node_data.query_variable_selector
        return variable_mapping

    def get_model_config(self, model: ModelConfig) -> tuple[ModelInstance, ModelConfigWithCredentialsEntity]:
        model_name = model.name
        provider_name = model.provider

        model_manager = ModelManager()
        model_instance = model_manager.get_model_instance(
            tenant_id=self.tenant_id, model_type=ModelType.LLM, provider=provider_name, model=model_name
        )

        provider_model_bundle = model_instance.provider_model_bundle
        model_type_instance = model_instance.model_type_instance
        model_type_instance = cast(LargeLanguageModel, model_type_instance)

        model_credentials = model_instance.credentials

        # check model
        provider_model = provider_model_bundle.configuration.get_provider_model(
            model=model_name, model_type=ModelType.LLM
        )

        if provider_model is None:
            raise ModelNotExistError(f"Model {model_name} not exist.")

        if provider_model.status == ModelStatus.NO_CONFIGURE:
            raise ModelCredentialsNotInitializedError(f"Model {model_name} credentials is not initialized.")
        elif provider_model.status == ModelStatus.NO_PERMISSION:
            raise ModelNotSupportedError(f"Dify Hosted OpenAI {model_name} currently not support.")
        elif provider_model.status == ModelStatus.QUOTA_EXCEEDED:
            raise ModelQuotaExceededError(f"Model provider {provider_name} quota exceeded.")

        # model config
        completion_params = model.completion_params
        stop = []
        if "stop" in completion_params:
            stop = completion_params["stop"]
            del completion_params["stop"]

        # get model mode
        model_mode = model.mode
        if not model_mode:
            raise ModelNotExistError("LLM mode is required.")

        model_schema = model_type_instance.get_model_schema(model_name, model_credentials)

        if not model_schema:
            raise ModelNotExistError(f"Model {model_name} not exist.")

        return model_instance, ModelConfigWithCredentialsEntity(
            provider=provider_name,
            model=model_name,
            model_schema=model_schema,
            mode=model_mode,
            provider_model_bundle=provider_model_bundle,
            credentials=model_credentials,
            parameters=completion_params,
            stop=stop,
        )

    def _get_prompt_template(self, node_data: KnowledgeRetrievalNodeData, metadata_fields: list, query: str):
        model_mode = ModelMode(node_data.metadata_model_config.mode)  # type: ignore
        input_text = query

        prompt_messages: list[LLMNodeChatModelMessage] = []
        if model_mode == ModelMode.CHAT:
            system_prompt_messages = LLMNodeChatModelMessage(
                role=PromptMessageRole.SYSTEM, text=METADATA_FILTER_SYSTEM_PROMPT
            )
            prompt_messages.append(system_prompt_messages)
            user_prompt_message_1 = LLMNodeChatModelMessage(
                role=PromptMessageRole.USER, text=METADATA_FILTER_USER_PROMPT_1
            )
            prompt_messages.append(user_prompt_message_1)
            assistant_prompt_message_1 = LLMNodeChatModelMessage(
                role=PromptMessageRole.ASSISTANT, text=METADATA_FILTER_ASSISTANT_PROMPT_1
            )
            prompt_messages.append(assistant_prompt_message_1)
            user_prompt_message_2 = LLMNodeChatModelMessage(
                role=PromptMessageRole.USER, text=METADATA_FILTER_USER_PROMPT_2
            )
            prompt_messages.append(user_prompt_message_2)
            assistant_prompt_message_2 = LLMNodeChatModelMessage(
                role=PromptMessageRole.ASSISTANT, text=METADATA_FILTER_ASSISTANT_PROMPT_2
            )
            prompt_messages.append(assistant_prompt_message_2)
            user_prompt_message_3 = LLMNodeChatModelMessage(
                role=PromptMessageRole.USER,
                text=METADATA_FILTER_USER_PROMPT_3.format(
                    input_text=input_text,
                    metadata_fields=json.dumps(metadata_fields, ensure_ascii=False),
                ),
            )
            prompt_messages.append(user_prompt_message_3)
            return prompt_messages
        elif model_mode == ModelMode.COMPLETION:
            return LLMNodeCompletionModelPromptTemplate(
                text=METADATA_FILTER_COMPLETION_PROMPT.format(
                    input_text=input_text,
                    metadata_fields=json.dumps(metadata_fields, ensure_ascii=False),
                )
            )

        else:
            raise InvalidModelTypeError(f"Model mode {model_mode} not support.")

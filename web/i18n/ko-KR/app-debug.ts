const translation = {
  pageTitle: {
    line1: '프롬프트',
    line2: '엔지니어링',
  },
  orchestrate: '오케스트레이션',
  promptMode: {
    simple: '전문가 모드로 전환하여 전체 프롬프트를 편집합니다',
    advanced: '전문가 모드',
    switchBack: '기본 모드로 전환',
    advancedWarning: {
      title: '전문가 모드로 전환되었습니다. 프롬프트를 변경하면 기본 모드로 돌아갈 수 없습니다.',
      description: '전문가 모드에서는 전체 프롬프트를 편집할 수 있습니다.',
      learnMore: '자세히 알아보기',
      ok: '확인',
    },
    operation: {
      addMessage: '메시지 추가',
    },
    contextMissing: '컨텍스트 컴포넌트를 찾을 수 없습니다. 프롬프트의 효과가 충분하지 않을 수 있습니다.',
  },
  operation: {
    applyConfig: '배포',
    resetConfig: '재설정',
    debugConfig: '디버그',
    addFeature: '기능 추가',
    automatic: '자동',
    stopResponding: '응답 중지',
    agree: '좋아요',
    disagree: '싫어요',
    cancelAgree: '좋아요 취소',
    cancelDisagree: '싫어요 취소',
    userAction: '사용자',
  },
  notSetAPIKey: {
    title: 'LLM 제공자 키가 설정되지 않았습니다',
    trailFinished: '트라이얼 종료',
    description: 'LLM 제공자 키가 설정되지 않았습니다. 디버깅하기 전에 설정해야 합니다.',
    settingBtn: '설정으로 이동',
  },
  trailUseGPT4Info: {
    title: '현재 gpt-4 는 지원되지 않습니다',
    description: 'gpt-4 를 사용하려면 API 키를 설정해야 합니다.',
  },
  feature: {
    groupChat: {
      title: '채팅 기능 강화',
      description: '사전 대화 설정을 추가하면 사용자 경험이 향상됩니다.',
    },
    groupExperience: {
      title: '경험 강화',
    },
    conversationOpener: {
      title: '대화 시작',
      description: '채팅 앱에서 AI 가 사용자에게 처음으로 적극적으로 말을 건다면 일반적으로 환영 메시지로 사용됩니다.',
    },
    suggestedQuestionsAfterAnswer: {
      title: '팔로우업',
      description: '다음 질문 제안을 설정하면 사용자에게 더 나은 채팅이 제공됩니다.',
      resDes: '사용자의 다음 질문에 대한 3 가지 제안.',
      tryToAsk: '질문해보세요',
    },
    moreLikeThis: {
      title: '유사한 항목',
      description: '여러 텍스트를 한 번에 생성하고 편집하여 계속해서 생성합니다.',
      generateNumTip: '생성 횟수',
      tip: '이 기능을 사용하면 추가적인 토큰 오버헤드가 발생합니다',
    },
    speechToText: {
      title: '음성에서 텍스트로',
      description: '활성화하면 음성 입력을 사용할 수 있습니다.',
      resDes: '음성 입력이 활성화되어 있습니다',
    },
    textToSpeech: {
      title: '텍스트에서 음성으로',
      description: '활성화하면 텍스트를 음성으로 변환할 수 있습니다.',
      resDes: '텍스트에서 오디오로의 변환이 활성화되어 있습니다',
    },
    citation: {
      title: '인용 및 소유권',
      description: '활성화하면 생성된 콘텐츠의 소스 문서 및 소유권 섹션이 표시됩니다.',
      resDes: '인용 및 소유권이 활성화되어 있습니다',
    },
    annotation: {
      title: '주석 응답',
      description: '유사한 사용자 질문과 우선 일치를 위해 캐시에 고품질 응답을 수동으로 추가할 수 있습니다.',
      resDes: '주석 응답이 활성화되어 있습니다',
      scoreThreshold: {
        title: '점수 임계값',
        description: '주석 응답의 유사성 임계값을 설정하는 데 사용됩니다.',
        easyMatch: '간단한 일치',
        accurateMatch: '정확한 일치',
      },
      matchVariable: {
        title: '매치 변수',
        choosePlaceholder: '매치 변수 선택',
      },
      cacheManagement: '주석',
      cached: '주석이 있는',
      remove: '삭제',
      removeConfirm: '이 주석을 삭제하시겠습니까?',
      add: '주석 추가',
      edit: '주석 편집',
    },
    dataSet: {
      title: '컨텍스트',
      noData: '지식을 컨텍스트로 가져올 수 있습니다',
      words: '단어',
      textBlocks: '텍스트 블록',
      selectTitle: '참조할 지식 선택',
      selected: '선택한 지식',
      noDataSet: '지식이 없습니다',
      toCreate: '생성하기',
      notSupportSelectMulti: '현재 다중 선택은 지원되지 않습니다',
      queryVariable: {
        title: '쿼리 변수',
        tip: '이 변수는 컨텍스트 조회에 사용되는 쿼리 입력으로 사용되며, 이 변수 입력에 관련된 컨텍스트 정보를 가져옵니다.',
        choosePlaceholder: '쿼리 변수 선택',
        noVar: '변수 없음',
        noVarTip: '변수 섹션 하단에서 변수를 생성하십시오',
        unableToQueryDataSet: '지식을 쿼리할 수 없음',
        unableToQueryDataSetTip: '지식 쿼리에 실패했습니다. 정상적으로 쿼리할 수 없는 경우, 컨텍스트 섹션에서 컨텍스트 쿼리 변수를 다시 선택하십시오.',
        ok: '확인',
        contextVarNotEmpty: '컨텍스트 쿼리 변수를 비울 수 없습니다',
        deleteContextVarTitle: '변수 "{{varName}}"를 삭제하시겠습니까?',
        deleteContextVarTip: '이 변수는 컨텍스트 쿼리 변수로 설정되어 있어 삭제하면 지식의 정상적인 사용에 영향을 미칩니다. 삭제하려면 컨텍스트 섹션에서 다시 선택하십시오.',
      },
    },
    tools: {
      title: '도구',
      tips: '도구는 사용자 입력이나 변수를 요청 매개변수로 사용하여 외부 데이터를 컨텍스트로 쿼리하는 표준적인 API 호출 방법을 제공합니다.',
      toolsInUse: '{{count}}개의 도구가 사용 중',
      modal: {
        title: '도구',
        toolType: {
          title: '도구 유형',
          placeholder: '도구 유형 선택',
        },
        name: {
          title: '이름',
          placeholder: '이름 입력',
        },
        variableName: {
          title: '변수 이름',
          placeholder: '변수 이름 입력',
        },
      },
    },
    conversationHistory: {
      title: '대화 기록',
      description: '대화 역할에 접두사 이름을 설정합니다',
      tip: '대화 기록이 활성화되어 있지 않습니다. 위의 프롬프트에 <histories>를 추가하십시오.',
      learnMore: '자세히 알아보기',
      editModal: {
        title: '대화 역할 이름 편집',
        userPrefix: '사용자 접두사',
        assistantPrefix: '어시스턴트 접두사',
      },
    },
    toolbox: {
      title: '도구 상자',
    },
    moderation: {
      title: '콘텐츠 모더레이션',
      description: '모더레이션 API 를 사용하거나 기밀 단어 목록을 유지함으로써 모델 출력을 안전하게 합니다.',
      allEnabled: '입력/출력 콘텐츠가 모두 활성화되어 있습니다',
      inputEnabled: '입력 콘텐츠가 활성화되어 있습니다',
      outputEnabled: '출력 콘텐츠가 활성화되어 있습니다',
      modal: {
        title: '콘텐츠 모더레이션 설정',
        provider: {
          title: '제공자',
          openai: 'OpenAI 모더레이션',
          openaiTip: {
            prefix: 'OpenAI 모더레이션에는',
            suffix: '에 OpenAI API 키가 설정되어 있어야 합니다.',
          },
          keywords: '키워드',
        },
        keywords: {
          tip: '한 줄에 하나씩, 줄 바꿈으로 입력하세요. 한 줄 당 최대 100 자.',
          placeholder: '한 줄씩 입력하세요',
          line: '줄',
        },
        content: {
          input: '입력 콘텐츠 모더레이션',
          output: '출력 콘텐츠 모더레이션',
          preset: '프리셋 응답',
          placeholder: '프리셋 응답 내용을 입력하세요',
          condition: '최소한 하나의 입력 및 출력 콘텐츠를 모더레이션합니다',
          fromApi: '프리셋 응답은 API 에서 반환됩니다',
          errorMessage: '프리셋 응답은 비워둘 수 없습니다',
          supportMarkdown: '마크다운이 지원됩니다',
        },
        openaiNotConfig: {
          before: 'OpenAI 모더레이션에는',
          after: '에 OpenAI API 키가 설정되어 있어야 합니다.',
        },
      },
    },
  },
  automatic: {
    title: '자동 어플리케이션 오케스트레이션',
    description: '시나리오를 설명하세요. Dify 가 어플리케이션을 자동으로 오케스트레이션 합니다.',
    intendedAudience: '누가 대상이 되는지 설명하세요.',
    intendedAudiencePlaceHolder: '예: 학생',
    solveProblem: '어떤 문제를 AI 가 해결할 것으로 예상하나요?',
    solveProblemPlaceHolder: '예: 학업 성적 평가',
    generate: '생성',
    audiencesRequired: '대상이 필요합니다',
    problemRequired: '문제가 필요합니다',
    resTitle: '다음 어플리케이션을 자동으로 오케스트레이션 했습니다.',
    apply: '이 오케스트레이션을 적용하기',
    noData: '왼쪽에 사용 예시를 기술하고, 오케스트레이션 미리보기가 여기에 나타납니다.',
    loading: '어플리케이션 오케스트레이션을 실행 중입니다...',
    overwriteTitle: '기존 구성을 덮어쓰시겠습니까?',
    overwriteMessage: '이 오케스트레이션을 적용하면 기존 구성이 덮어쓰여집니다.',
  },
  resetConfig: {
    title: '리셋을 확인하시겠습니까?',
    message: '변경 사항이 취소되고, 마지막으로 공개된 구성이 복원됩니다.',
  },
  errorMessage: {
    nameOfKeyRequired: '키 이름: {{key}} 이 필요합니다',
    valueOfVarRequired: '{{key}}의 값은 비워둘 수 없습니다',
    queryRequired: '요청 텍스트가 필요합니다.',
    waitForResponse: '이전 메시지에 대한 응답이 완료될 때까지 기다려 주세요.',
    waitForBatchResponse: '배치 작업에 대한 응답이 완료될 때까지 기다려 주세요.',
    notSelectModel: '모델을 선택해 주세요',
    waitForImgUpload: '이미지 업로드가 완료될 때까지 기다려 주세요',
  },
  chatSubTitle: '단계',
  completionSubTitle: '접두사 프롬프트',
  promptTip: '프롬프트는 AI 의 응답을 지시하고 제한하여 유도합니다. {{input}}과 같은 변수를 삽입하세요. 이 프롬프트는 사용자에게 표시되지 않습니다.',
  formattingChangedTitle: '포맷이 변경되었습니다',
  formattingChangedText: '포맷을 변경하면 디버그 영역이 재설정됩니다. 계속하시겠습니까?',
  variableTitle: '변수',
  variableTip: '사용자는 양식에 변수를 입력하고, 프롬프트 내의 변수가 자동으로 대체됩니다.',
  notSetVar: '변수를 사용하면 사용자는 양식에 입력할 때 프롬프트의 단어나 시작 단어를 소개할 수 있습니다. "{{input}}"을 프롬프트 단어에 입력해 보세요.',
  autoAddVar: '프리프롬프트에서 참조되는 미정의 변수가 있습니다. 사용자 입력 양식에 추가하시겠습니까?',
  variableTable: {
    key: '변수 키',
    name: '사용자 입력 필드명',
    optional: '옵션',
    type: '입력 타입',
    action: '액션',
    typeString: '문자열',
    typeSelect: '선택',
  },
  varKeyError: {
    canNoBeEmpty: '{{key}}가 필요합니다',
    tooLong: '{{key}}가 너무 깁니다. 30 자를 넘을 수 없습니다',
    notValid: '{{key}}가 유효하지 않습니다. 문자, 숫자, 밑줄만 포함할 수 있습니다',
    notStartWithNumber: '{{key}}는 숫자로 시작할 수 없습니다',
    keyAlreadyExists: '{{key}}는 이미 존재합니다',
  },
  otherError: {
    promptNoBeEmpty: '프롬프트를 비울 수 없습니다',
    historyNoBeEmpty: '프롬프트에 대화 기록을 설정해야 합니다',
    queryNoBeEmpty: '프롬프트에 쿼리를 설정해야 합니다',
  },
  variableConfig: {
    'addModalTitle': '입력 필드 추가',
    'editModalTitle': '입력 필드 편집',
    'description': '{{varName}} 변수 설정',
    'fieldType': '필드 타입',
    'string': '짧은 텍스트',
    'text-input': '짧은 텍스트',
    'paragraph': '문단',
    'select': '선택',
    'number': '숫자',
    'notSet': '설정되지 않음. 프롬프트의 프리픽스에 {{input}}을 입력해 보세요.',
    'stringTitle': '폼 텍스트 상자 옵션',
    'maxLength': '최대 길이',
    'options': '옵션',
    'addOption': '옵션 추가',
    'apiBasedVar': 'API 기반 변수',
    'varName': '변수명',
    'labelName': '레이블명',
    'inputPlaceholder': '입력하세요',
    'required': '필수',
    'hide': '숨기기',
    'errorMsg': {
      varNameRequired: '변수명은 필수입니다',
      labelNameRequired: '레이블명은 필수입니다',
      varNameCanBeRepeat: '변수명은 중복될 수 없습니다',
      atLeastOneOption: '적어도 하나의 옵션이 필요합니다',
      optionRepeat: '옵션이 중복되어 있습니다',
    },
    'defaultValue': '기본값',
    'noDefaultValue': '기본값 없음',
    'selectDefaultValue': '기본값 선택',
  },
  vision: {
    name: '비전',
    description: '비전을 활성화하면 모델이 이미지를 받아와 관련 질문에 답변할 수 있습니다.',
    settings: '설정',
    visionSettings: {
      title: '비전 설정',
      resolution: '해상도',
      resolutionTooltip: `저해상도는 모델에게 512 x 512 해상도의 저해상도 이미지를 제공하여 65 토큰의 예산으로 이미지를 표현합니다. 이로 인해 API 는 더 빠른 응답을 제공하며 높은 세부 정보가 필요한 경우 토큰 소모를 늘립니다.
      \n
      고해상도는 먼저 모델에게 저해상도 이미지를 보여주고, 그 후 입력 이미지 크기에 따라 512px 의 정사각형 세부 사진을 만듭니다. 각 세부 사진에 대해 129 토큰의 예산을 사용합니다.`,
      high: '고',
      low: '저',
      uploadMethod: '업로드 방식',
      both: '모두',
      localUpload: '로컬 업로드',
      url: 'URL',
      uploadLimit: '업로드 제한',
    },
  },
  voice: {
    name: '음성',
    defaultDisplay: '기본 음성',
    description: '텍스트 읽기 음성 설정',
    settings: '설정',
    voiceSettings: {
      title: '음성 설정',
      language: '언어',
      resolutionTooltip: '텍스트 읽기 음성 언어를 지원합니다.',
      voice: '음성',
      autoPlay: '자동 재생',
      autoPlayEnabled: '켜다',
      autoPlayDisabled: '폐쇄',
    },
  },
  openingStatement: {
    title: '대화 시작',
    add: '추가',
    writeOpener: '오프너 작성',
    placeholder: '여기에 오프너 메시지를 작성하세요. 변수를 사용할 수 있습니다. {{variable}}를 입력해보세요.',
    openingQuestion: '시작 질문',
    openingQuestionPlaceholder: '변수를 사용할 수 있습니다. {{variable}}을(를) 입력해 보세요.',
    noDataPlaceHolder: '사용자와의 대화를 시작하면 대화 애플리케이션에서 그들과 더 밀접한 관계를 구축하는 데 도움이 됩니다.',
    varTip: '변수를 사용할 수 있습니다. {{variable}}를 입력해보세요.',
    tooShort: '대화 시작에는 최소 20 단어의 초기 프롬프트가 필요합니다.',
    notIncludeKey: '초기 프롬프트에 변수 {{key}}가 포함되어 있지 않습니다. 초기 프롬프트에 추가하세요.',
  },
  modelConfig: {
    model: '모델',
    setTone: '응답 톤 설정',
    title: '모델 및 매개변수',
    modeType: {
      chat: '채팅',
      completion: '완성',
    },
  },
  inputs: {
    title: '디버그 및 미리보기',
    noPrompt: '프리프롬프트 입력란에 몇 가지 프롬프트를 작성해보세요.',
    userInputField: '사용자 입력 필드',
    noVar: '변수 값을 입력하세요. 새로운 세션이 시작될 때마다 프롬프트 단어가 자동으로 대체됩니다.',
    chatVarTip: '변수 값을 입력하세요. 새로운 세션이 시작될 때마다 프롬프트 단어가 자동으로 대체됩니다.',
    completionVarTip: '변수 값을 입력하세요. 질문이 전송될 때마다 프롬프트 단어가 자동으로 대체됩니다.',
    previewTitle: '프롬프트 미리보기',
    queryTitle: '쿼리 내용',
    queryPlaceholder: '요청 텍스트를 입력하세요.',
    run: '실행',
  },
  result: '출력 텍스트',
  datasetConfig: {
    settingTitle: '리트리벌 설정',
    knowledgeTip: '지식을 추가하려면 "+" 버튼을 클릭하세요.',
    retrieveOneWay: {
      title: 'N-to-1 리트리벌',
      description: '사용자 의도와 지식 설명을 기반으로, 에이전트가 자율적으로 최적의 지식을 선택합니다. 개별적이고 제한된 지식을 가진 애플리케이션에 적합합니다.',
    },
    retrieveMultiWay: {
      title: '멀티패스 리트리벌',
      description: '사용자 의도에 따라 모든 지식을 쿼리하고, 관련 텍스트를 여러 소스에서 가져와 다시 순위를 매긴 후 사용자 쿼리에 가장 적합한 결과를 선택합니다. 재순위 모델 API 의 구성이 필요합니다.',
    },
    rerankModelRequired: '재순위 모델이 필요합니다',
    params: '매개변수',
    top_k: '상위 K',
    top_kTip: '사용자 질문에 가장 유사한 청크를 필터링하는 데 사용됩니다. 시스템은 선택한 모델의 max_tokens 에 따라 동적으로 상위 K 값을 조정합니다.',
    score_threshold: '점수 임계값',
    score_thresholdTip: '청크 필터링의 유사성 임계값을 설정하는 데 사용됩니다.',
    retrieveChangeTip: '인덱스 모드 및 리트리벌 모드를 변경하면 이 지식과 관련된 애플리케이션에 영향을 줄 수 있습니다.',
  },
  debugAsSingleModel: '단일 모델로 디버그',
  debugAsMultipleModel: '다중 모델로 디버그',
  duplicateModel: '복제',
  publishAs: '로 게시',
  assistantType: {
    name: '어시스턴트 유형',
    chatAssistant: {
      name: '기본 어시스턴트',
      description: '대규모 언어 모델을 사용하여 채팅 기반의 어시스턴트를 구축합니다',
    },
    agentAssistant: {
      name: '에이전트 어시스턴트',
      description: '작업을 자율적으로 완료하기 위한 도구를 선택할 수 있는 인텔리전트 에이전트를 구축합니다',
    },
  },
  agent: {
    agentMode: '에이전트 모드',
    agentModeDes: '에이전트의 추론 모드 유형을 설정합니다',
    agentModeType: {
      ReACT: 'ReAct',
      functionCall: '함수 호출',
    },
    setting: {
      name: '에이전트 설정',
      description: '에이전트 어시스턴트 설정에서는 에이전트 모드나 빌트인 프롬프트 등 고급 기능을 설정할 수 있습니다. 에이전트 유형에서만 사용할 수 있습니다.',
      maximumIterations: {
        name: '최대 반복 횟수',
        description: '에이전트 어시스턴트가 실행할 수 있는 반복 횟수를 제한합니다',
      },
    },
    buildInPrompt: '빌트인 프롬프트',
    firstPrompt: '첫 번째 프롬프트',
    nextIteration: '다음 반복',
    promptPlaceholder: '여기에 프롬프트를 입력하세요',
    tools: {
      name: '도구',
      description: '도구를 사용하여 인터넷 검색이나 과학적 계산 등 LLM 의 기능을 확장할 수 있습니다',
      enabled: '활성화됨',
    },
  },
}

export default translation

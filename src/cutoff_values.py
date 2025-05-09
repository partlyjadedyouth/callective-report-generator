"""
# cutoff_values.py
# 다양한 심리검사 및 직무 스트레스 점수의 절단점을 저장하는 모듈

# 번아웃 관련 절단점
# [정상-준위험, 준위험-위험] 값으로 구성
"""

# 번아웃 핵심 증상 절단점
CUTOFF_BURNOUT_PRIMARY = [2.58, 3.01]
CUTOFF_BURNOUT_EXHAUSTION = [3.05, 3.30]
CUTOFF_BURNOUT_DEPERSONALIZATION = [2.09, 3.29]
CUTOFF_BURNOUT_COGNITIVE_REGULATION = [2.69, 3.09]
CUTOFF_BURNOUT_EMOTIONAL_REGULATION = [2.29, 2.89]

# 번아웃 2차적 증상 절단점
CUTOFF_BURNOUT_SECONDARY = [2.84, 3.34]

# 직무 스트레스 절단점
# [정상-준위험, 준위험-위험] 값으로 구성
CUTOFF_STRESS = [50.0, 55.6]

# 감정 노동 절단점
# 각 항목별 위험 기준점
CUTOFF_EMOTIONAL_LABOR = [76.66, 72.21, 63.88, 49.99, 45.23]

# 직무 스트레스 요인 절단점
# [하위 50% 중 큰 값, 상위 50% 중 큰 값] 구성
CUTOFF_JOB_DEMAND = [58.3, 66.6]  # 직무요구
CUTOFF_INSUFFICIENT_JOB_CONTROL = [58.3, 60.0]  # 직무자율성 결여
CUTOFF_INTERPERSONAL_CONFLICT = [33.3, 44.4]  # 관계갈등
CUTOFF_JOB_INSECURITY = [33.3, 50.0]  # 직무불안정
CUTOFF_ORGANIZATIONAL_SYSTEM = [50.0, 66.6]  # 조직체계
CUTOFF_LACK_OF_REWARD = [55.5, 66.6]  # 보상부적절
CUTOFF_OCCUPATIONAL_CLIMATE = [41.6, 50.0]  # 직장문화

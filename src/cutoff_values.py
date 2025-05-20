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

# 감정 노동 절단점
# 각 항목별 위험 기준점
# 남녀 차이가 있는 경우 남녀 차이 절단점 추가
CUTOFF_EMOTIONAL_LABOR = [76.66, 72.21, 63.88, 49.99, 45.23]  # 여성
CUTOFF_EMOTIONAL_LABOR_MALE = [83.32, 83.32, 69.43, 61.10, 49.99]  # 남성

# 직무 스트레스 절단점
# [정상-준위험, 준위험-위험] 값으로 구성
# 남녀 차이
CUTOFF_STRESS = [50.0, 55.6]  # 여성
CUTOFF_STRESS_MALE = [48.4, 54.7]  # 남성

# 직무 스트레스 요인 절단점
CUTOFF_JOB_DEMAND = [58.3, 66.6]  # 직무요구 - 여성
CUTOFF_INSUFFICIENT_JOB_CONTROL = [58.3, 60.0]  # 직무자율성 결여 - 여성
CUTOFF_INTERPERSONAL_CONFLICT = [33.3, 44.4]  # 관계갈등 - 여성
CUTOFF_JOB_INSECURITY = [33.3, 50.0]  # 직무불안정 - 여성
CUTOFF_ORGANIZATIONAL_SYSTEM = [50.0, 66.6]  # 조직체계 - 여성
CUTOFF_LACK_OF_REWARD = [55.5, 66.6]  # 보상부적절 - 여성
CUTOFF_OCCUPATIONAL_CLIMATE = [41.6, 50.0]  # 직장문화 - 여성

# 직무 스트레스 요인 절단점 (남성)
CUTOFF_JOB_DEMAND_MALE = [50.0, 58.3]  # 직무요구 - 남성
CUTOFF_INSUFFICIENT_JOB_CONTROL_MALE = [50.0, 66.6]  # 직무자율성 결여 - 남성
CUTOFF_INTERPERSONAL_CONFLICT_MALE = [33.3, 44.4]  # 관계갈등 - 남성
CUTOFF_JOB_INSECURITY_MALE = [50.0, 66.6]  # 직무불안정 - 남성
CUTOFF_ORGANIZATIONAL_SYSTEM_MALE = [50.0, 66.6]  # 조직체계 - 남성
CUTOFF_LACK_OF_REWARD_MALE = [55.5, 66.6]  # 보상부적절 - 남성
CUTOFF_OCCUPATIONAL_CLIMATE_MALE = [41.6, 50.0]  # 직장문화 - 남성

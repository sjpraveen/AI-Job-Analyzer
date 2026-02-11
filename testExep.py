from src.common.custom_exception import CustomException

try:
    x=1/0
except Exception as e:
    raise CustomException("1 divided by zero not possible", e)
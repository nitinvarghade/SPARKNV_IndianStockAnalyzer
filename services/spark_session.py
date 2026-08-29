try:
    from pyspark.sql import SparkSession
except ImportError:
    SparkSession = None


def create_spark_session():

    if SparkSession is None:
        raise ImportError(
            "PySpark is not installed. "
            "Install it using: pip install pyspark"
        )

    return (
        SparkSession.builder
        .appName("IndianStockAnalyzer")
        .getOrCreate()
    )
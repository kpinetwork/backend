import sys
import uuid
import json
import logging
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql import SparkSession
from awsglue.dynamicframe import DynamicFrame
import boto3
from pyspark.sql.types import (
    DateType,
    StructType,
    StructField,
    StringType,
    BooleanType,
    DoubleType,
)

logging.basicConfig()
logger = logging.getLogger("logger")
logger.setLevel(logging.WARNING)
glueContext = GlueContext(SparkContext.getOrCreate())
spark = SparkSession.builder.getOrCreate()

time_period_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("start_at", StringType(), False),
        StructField("end_at", StringType(), False),
    ]
)

scenario_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("name", StringType(), False),
        StructField("currency", StringType(), False),
        StructField("type", StringType(), False),
        StructField("period_id", StringType(), False),
        StructField("company_id", StringType(), False),
    ]
)

metric_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("name", StringType(), False),
        StructField("value", DoubleType(), False),
        StructField("type", StringType(), False),
        StructField("data_type", StringType(), False),
        StructField("period_id", StringType(), False),
        StructField("company_id", StringType(), False),
    ]
)

currency_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("currency_iso_code", StringType(), False),
        StructField("metric_id", StringType(), False),
    ]
)

scenario_metric_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("metric_id", StringType(), False),
        StructField("scenario_id", StringType(), False),
    ]
)

company_schema = StructType(
    [
        StructField("id", StringType(), False),
        StructField("name", StringType(), False),
        StructField("sector", StringType(), False),
        StructField("vertical", StringType(), True),
        StructField("inves_profile_name", StringType(), True),
        StructField("is_public", BooleanType(), False),
    ]
)


def existing_ids_from_database(env, db_table):
    database = "kpinetworkdb"
    if env == "demo":
        database = "demokpinetworkdb"

    ctg_connection = "{}_connection".format(env)
    catalog_connection = glueContext.extract_jdbc_conf(ctg_connection)

    dynamic_frame = glueContext.create_dynamic_frame.from_options(
        connection_type="postgresql",
        connection_options={
            "url": "{}/{}".format(catalog_connection["url"], database),
            "user": catalog_connection["user"],
            "password": catalog_connection["password"],
            "dbtable": db_table,
        },
    )
    dynamic_frame = dynamic_frame.toDF().createOrReplaceTempView(
        "{}_table".format(db_table)
    )
    sqldf = spark.sql("SELECT id FROM {}_table".format(db_table))
    result_from_sqldf = sqldf.collect()
    ids_from_db = [row.id for row in result_from_sqldf]
    return ids_from_db


def read_table_from_database(env, database, db_table):
    ctg_connection = "{}_connection".format(env)
    catalog_connection = glueContext.extract_jdbc_conf(ctg_connection)

    return glueContext.create_dynamic_frame.from_options(
        connection_type="postgresql",
        connection_options={
            "url": "{}/{}".format(catalog_connection["url"], database),
            "user": catalog_connection["user"],
            "password": catalog_connection["password"],
            "dbtable": db_table,
        },
    )


def create_temp_table(dynamic_frame, table_name):
    return dynamic_frame.toDF().createOrReplaceTempView(table_name)


def existing_metric_from_file(env, company_id, scenario_name, metric_name):
    resultant_metric_id = None
    database = "kpinetworkdb"
    if env == "demo":
        database = "demokpinetworkdb"

    dynamic_scenario_frame = read_table_from_database(
        env, database, "financial_scenario"
    )
    dynamic_scenario_frame = create_temp_table(
        dynamic_scenario_frame, "financial_scenario_table"
    )
    scenario_dataframe = spark.sql(
        "SELECT id FROM financial_scenario_table WHERE company_id = '{}' AND name = '{}'".format(
            company_id, scenario_name
        )
    )
    result_scenario_dataframe = scenario_dataframe.collect()
    scenario_ids = [row.id for row in result_scenario_dataframe]

    if not scenario_ids:
        return resultant_metric_id

    financial_scenario_id = scenario_ids[0]
    dynamic_sm_frame = read_table_from_database(env, database, "scenario_metric")
    dynamic_sm_frame = create_temp_table(dynamic_sm_frame, "scenario_metric_table")
    sm_dataframe = spark.sql(
        "SELECT metric_id FROM scenario_metric_table WHERE scenario_id = '{}'".format(
            financial_scenario_id
        )
    )
    result_sm_dataframe = sm_dataframe.collect()
    sm_ids = [row.metric_id for row in result_sm_dataframe]

    if not sm_ids:
        return resultant_metric_id

    sc_metric_ids = sm_ids
    for sc_metric_id in sc_metric_ids:
        metric_id = sc_metric_id
        dynamic_m_frame = read_table_from_database(env, database, "metric")
        dynamic_m_frame = create_temp_table(dynamic_m_frame, "metric_table")
        metrics_dataframe = spark.sql(
            "SELECT * FROM metric_table WHERE id = '{}' AND name = '{}'".format(
                metric_id, metric_name
            )
        )
        result_metrics_dataframe = metrics_dataframe.collect()
        metrics_ids = [row for row in result_metrics_dataframe]

        if metrics_ids:
            resultant_metric_id = metrics_ids
            break

    return resultant_metric_id


def validate_existing_metric_from_dataframe(env, metric_id):
    result = False
    database = "kpinetworkdb"
    if env == "demo":
        database = "demokpinetworkdb"

    dynamic_metrics_frame = read_table_from_database(env, database, "metric")
    dynamic_metrics_frame = create_temp_table(dynamic_metrics_frame, "metric_table")
    metrics_dataframe = spark.sql(
        "SELECT * FROM metric_table WHERE id = '{}'".format(metric_id)
    )
    result_metrics_dataframe = metrics_dataframe.collect()
    if result_metrics_dataframe:
        result = True

    return result


def save_to_database(env, db_table, dataframe):
    database = "kpinetworkdb"
    if env == "demo":
        database = "demokpinetworkdb"

    logger.warning("==========Save in Database===============================")
    logger.warning("env: {} database: {} db_table: {}".format(env, database, db_table))

    dynamic_frame = DynamicFrame.fromDF(dataframe, glueContext, db_table)
    glueContext.write_dynamic_frame.from_jdbc_conf(
        dynamic_frame,
        catalog_connection="{}_connection".format(env),
        connection_options={"dbtable": db_table, "database": database},
    )


def get_data_from_dataframe(dataframe):
    headers = dataframe.columns
    data = dataframe.collect()
    return (headers, data)


def get_index_limits(row):
    return [i for i in range(0, len(row)) if row[i] and row[i].startswith(":")]


def get_row_value(row, column):
    if column in row:
        return row[column]
    return None


def is_valid_value(value):
    return value is not None and value.strip()


def get_metric_value(value):
    try:
        return float(value)
    except Exception as error:
        logger.warning(error)
        return None


def get_name(row, index):
    cell = row[index]
    return cell.split(":")[1]


def get_limits(limits, count):
    index_limits = []
    for index in range(len(limits)):
        max_index = len(limits) - 1
        next_index = count if max_index == index else limits[index + 1]
        index_limits.append((limits[index], next_index))

    return index_limits


def get_company_description(row, env):
    existing_id = existing_ids_from_database(env, "company")
    id_from_file = get_row_value(row, "Unique ID")
    if id_from_file in existing_id:
        company_id = id_from_file
    else:
        company_id = str(uuid.uuid4())
    name = get_row_value(row, "Name")
    sector = get_row_value(row, "Sector")
    vertical = get_row_value(row, "Vertical")
    inves_profile = get_row_value(row, "Investor profile")

    return [
        company_id,
        name,
        sector,
        vertical,
        inves_profile,
        True,
    ]


def get_time_period(start, end):
    return [str(uuid.uuid4()), start, end]


def get_scenario(name, scenario_type, period, company):
    return [str(uuid.uuid4()), name, "USD", scenario_type, period, company]


def get_metric(name, value, period, company):
    return [str(uuid.uuid4()), name, value, "standard", "currency", period, company]


def get_existing_metric(row, name, value, company):
    return [
        str(row[0].id),
        name,
        value,
        "standard",
        "currency",
        str(row[0].period_id),
        company,
    ]


def get_time_period_str(year):
    start = "{}-01-01".format(year)
    end = "{}-12-31".format(year)
    return (start, end)


def get_scenario_data(year, scenario_type, company, scenarios, periods):

    scenario_name = "{}-{}".format(scenario_type, year)
    start_time, end_time = get_time_period_str(year)
    time_period = []
    scenario = []

    scenario_created = list(
        filter(lambda scenario: scenario[1] == scenario_name, scenarios)
    )

    if len(scenario_created) > 0:
        scenario = scenario_created[0]
        time_period.append(scenario[4])

    else:
        time_period = get_time_period(start_time, end_time)
        periods.append(time_period)

        scenario = get_scenario(
            scenario_name, scenario_type, time_period[0], company[0]
        )
        scenarios.append(scenario)

    return (time_period, scenario)


def get_metric_data(metric_name, period_id, scenario_id, company_id, value):
    metric = get_metric(metric_name, value, period_id, company_id)

    currency_metric = [str(uuid.uuid4()), "USD", metric[0]]

    scenario_metric = [str(uuid.uuid4()), metric[0], scenario_id]

    return (metric, currency_metric, scenario_metric)


def get_updating_metric_data(row, metric_name, company_id, value):
    metric = get_existing_metric(row, metric_name, value, company_id)
    return metric


def get_financial_data(
    row, metric_limits, scenarios_index, header, years_row, metric_row, company, env
):

    periods, scenarios, metrics, scenario_metrics, currencies = [], [], [], [], []
    scenario_type = ""

    for limits in metric_limits:
        start, end = limits
        metric_name = get_name(metric_row, start)
        if start in scenarios_index:
            scenario_type = get_name(header, start)

        for index in range(start, end):
            metric_value = row[index]
            year = years_row[index]
            value = get_metric_value(metric_value)

            if is_valid_value(metric_value) and value is not None:
                metric_and_year = scenario_type + "-" + year
                metric_exists = existing_metric_from_file(
                    env, company[0], metric_and_year, metric_name
                )

                if metric_exists is None:
                    time_period, scenario = get_scenario_data(
                        year, scenario_type, company, scenarios, periods
                    )

                    metric, currency, scenario_metric = get_metric_data(
                        metric_name, time_period[0], scenario[0], company[0], value
                    )
                    metrics.append(metric)
                    currencies.append(currency)
                    scenario_metrics.append(scenario_metric)
                else:
                    metric = get_updating_metric_data(
                        metric_exists, metric_name, company[0], value
                    )
                    metrics.append(metric)

    return (periods, scenarios, metrics, scenario_metrics, currencies)


def get_company_financial_data(
    row, metric_limits, scenarios_index, header, years_row, metric_row, env
):

    companies = []

    company = get_company_description(row, env)
    companies.append(company)

    periods, scenarios, metrics, scenario_metrics, currencies = get_financial_data(
        row, metric_limits, scenarios_index, header, years_row, metric_row, company, env
    )

    return (companies, periods, scenarios, metrics, scenario_metrics, currencies)


def get_schemas_data_from_dataframe(headers, data, env):
    data_periods = []
    data_metrics = []
    data_companies = []
    data_scenarios = []
    data_currencies = []
    data_scenario_metrics = []

    metric_row = data[0]
    metric_limits = get_limits(get_index_limits(metric_row), len(headers))
    scenarios_index = get_index_limits(headers)

    for index in range(2, len(data)):
        if not is_valid_value(data[index][0]):
            (
                _companies,
                _periods,
                _scenarios,
                _metrics,
                _scenario_metrics,
                _currencies,
            ) = get_company_financial_data(
                data[index],
                metric_limits,
                scenarios_index,
                headers,
                data[1],
                metric_row,
                env,
            )
            data_periods.extend(_periods)
            data_companies.extend(_companies)
            data_scenarios.extend(_scenarios)
            data_metrics.extend(_metrics)
            data_scenario_metrics.extend(_scenario_metrics)
            data_currencies.extend(_currencies)

    return (
        data_companies,
        data_periods,
        data_scenarios,
        data_metrics,
        data_scenario_metrics,
        data_currencies,
    )


def get_existing_schemas_data_from_dataframe(headers, data, env):
    data_periods = []
    data_metrics = []
    data_companies = []
    data_scenarios = []
    data_currencies = []
    data_scenario_metrics = []

    metric_row = data[0]
    metric_limits = get_limits(get_index_limits(metric_row), len(headers))
    scenarios_index = get_index_limits(headers)

    for index in range(2, len(data)):
        ids = existing_ids_from_database(env, "company")
        if is_valid_value(data[index][0]) and data[index][0] in ids:
            (
                _companies,
                _periods,
                _scenarios,
                _metrics,
                _scenario_metrics,
                _currencies,
            ) = get_company_financial_data(
                data[index],
                metric_limits,
                scenarios_index,
                headers,
                data[1],
                metric_row,
                env,
            )
            data_periods.extend(_periods)
            data_companies.extend(_companies)
            data_scenarios.extend(_scenarios)
            data_metrics.extend(_metrics)
            data_scenario_metrics.extend(_scenario_metrics)
            data_currencies.extend(_currencies)

    return (
        data_companies,
        data_periods,
        data_scenarios,
        data_metrics,
        data_scenario_metrics,
        data_currencies,
    )


def dataframe_cast_date_type(data_frame, columns):
    for column in columns:
        data_frame = data_frame.withColumn(column, data_frame[column].cast(DateType()))

    return data_frame


def get_dataframes_from_lists(data):
    (companies, periods, scenarios, metrics, scenario_metrics, currencies) = data

    df_companies = spark.createDataFrame(companies, schema=company_schema)
    df_time_periods = spark.createDataFrame(periods, schema=time_period_schema)
    df_time_periods = dataframe_cast_date_type(df_time_periods, ["start_at", "end_at"])
    df_scenarios = spark.createDataFrame(scenarios, schema=scenario_schema)
    df_metrics = spark.createDataFrame(metrics, schema=metric_schema)
    df_currencies = spark.createDataFrame(currencies, schema=currency_schema)
    df_scenario_metrics = spark.createDataFrame(
        scenario_metrics, schema=scenario_metric_schema
    )

    return (
        df_companies,
        df_time_periods,
        df_scenarios,
        df_metrics,
        df_scenario_metrics,
        df_currencies,
    )


def get_updating_dataframes_from_lists(data):
    (companies, periods, scenarios, metrics, scenario_metrics, currencies) = data

    df_companies = spark.createDataFrame(companies, schema=company_schema)
    df_time_periods = spark.createDataFrame(periods, schema=time_period_schema)
    df_time_periods = dataframe_cast_date_type(df_time_periods, ["start_at", "end_at"])
    df_scenarios = spark.createDataFrame(scenarios, schema=scenario_schema)
    df_metrics = spark.createDataFrame(metrics, schema=metric_schema)
    df_currencies = spark.createDataFrame(currencies, schema=currency_schema)
    df_scenario_metrics = spark.createDataFrame(
        scenario_metrics, schema=scenario_metric_schema
    )

    return (
        df_companies,
        df_time_periods,
        df_scenarios,
        df_metrics,
        df_scenario_metrics,
        df_currencies,
    )


def call_lambda_to_update(env, data):
    name = name = "{}_update_data_lambda_function".format(env)
    client = boto3.client("lambda")
    body = json.dumps(data)
    event = {"body": body}

    client.invoke(FunctionName=name, Payload=json.dumps(event))


def update_data_to_database(data, env):
    (
        df_companies,
        df_time_periods,
        df_scenarios,
        df_metrics,
        df_scenario_metrics,
        df_currencies,
    ) = get_updating_dataframes_from_lists(data)

    logger.warning("==========Company===============================")
    df_companies.show()
    companies_updatables = df_companies.rdd.map(lambda x: x.asDict()).collect()

    logger.warning("==========Existing Metrics===============================")
    result_metrics_df = df_metrics.collect()

    new_metrics = []
    existing_metrics = []
    for row in result_metrics_df:
        if validate_existing_metric_from_dataframe(env, row.id):
            existing_metrics.append(row)
        else:
            new_metrics.append(row)
    df_existing_metrics = spark.createDataFrame(existing_metrics, schema=metric_schema)
    df_new_metrics = spark.createDataFrame(new_metrics, schema=metric_schema)
    df_existing_metrics.show()

    metrics_updatables = df_existing_metrics.rdd.map(lambda x: x.asDict()).collect()
    data_to_update = {"companies": companies_updatables, "metrics": metrics_updatables}
    call_lambda_to_update(env, data_to_update)

    if (
        df_new_metrics.collect()
        and df_time_periods.collect()
        and df_scenarios.collect()
        and df_scenario_metrics.collect()
        and df_currencies.collect()
    ):
        logger.warning("==========Time Period============================")
        df_time_periods.show()
        save_to_database(env, "time_period", df_time_periods)

        logger.warning("==========Scenario===============================")
        df_scenarios.show()
        save_to_database(env, "financial_scenario", df_scenarios)

        logger.warning("==========New Metric===============================")
        df_new_metrics.show()
        save_to_database(env, "metric", df_new_metrics)

        logger.warning("==========Currency==============================")
        df_currencies.show()
        save_to_database(env, "currency", df_currencies)

        logger.warning("==========Scenario Metric========================")
        df_scenario_metrics.show()
        save_to_database(env, "scenario_metric", df_scenario_metrics)


def save_data_to_database(data, env):

    (
        df_companies,
        df_time_periods,
        df_scenarios,
        df_metrics,
        df_scenario_metrics,
        df_currencies,
    ) = get_dataframes_from_lists(data)

    logger.warning("==========Company===============================")
    df_companies.show()
    save_to_database(env, "company", df_companies)

    logger.warning("==========Time period===========================")
    df_time_periods.show()
    save_to_database(env, "time_period", df_time_periods)

    logger.warning("==========Financial scenario====================")
    df_scenarios.show()
    save_to_database(env, "financial_scenario", df_scenarios)

    logger.warning("==========Metric================================")
    df_metrics.show()
    save_to_database(env, "metric", df_metrics)

    logger.warning("==========Currency metric=======================")
    df_currencies.show()
    save_to_database(env, "currency_metric", df_currencies)

    logger.warning("==========Scenario metric=======================")
    df_scenario_metrics.show()
    save_to_database(env, "scenario_metric", df_scenario_metrics)


def get_dataframe_from_file(file_path):

    logger.warning("file path: {}".format(file_path))

    file_dataframe = (
        spark.read.format("csv")
        .option("header", "true")
        .option("delimiter", ",")
        .load(file_path)
    )
    return file_dataframe


def proccess_file(file_path, env):
    dataframe = get_dataframe_from_file(file_path)
    headers, data = get_data_from_dataframe(dataframe)

    logger.warning("==========File Headers===============================")
    logger.warning(headers)

    logger.warning("==========New File Data===============================")
    schemas_data = get_schemas_data_from_dataframe(headers, data, env)
    save_data_to_database(schemas_data, env)

    logger.warning("==========existing Data===============================")
    schemas_existing_data = get_existing_schemas_data_from_dataframe(headers, data, env)
    update_data_to_database(schemas_existing_data, env)


def start_job(env, file_name, bucket_name):
    file_path = "s3://{}/{}".format(bucket_name, file_name)

    logger.warning(file_path)
    logger.warning("env: {}".format(env))

    proccess_file(file_path, env)


def get_values_from_dynamic_df(dynamic_df, user, file):
    df = dynamic_df.toDF()
    df.show()
    df = df.filter((df.user_id == user) & (df.file_name == file))
    df.show()
    result = df.first()

    if result:
        return (result.connection_id, result.user_id, result.file_name)
    return ("", "", "")


def get_connection_option_to_read(catalog_connection, database):
    return {
        "url": "{}/{}".format(catalog_connection["url"], database),
        "user": catalog_connection["user"],
        "password": catalog_connection["password"],
        "dbtable": "websocket",
    }


def get_user_and_file(filename):
    file = filename.split(".csv")[0]
    attrs = file.split(":")
    return attrs[1]


def call_lambda(env, user, file, connection_id):
    name = "{}_message_lambda_function".format(env)
    client = boto3.client("lambda")
    data = json.dumps({"file": file, "connection_id": connection_id, "user": user})
    event = {"requestContext": {"connectionId": connection_id}, "body": data}

    client.invoke(FunctionName=name, Payload=json.dumps(event))


def read_websocket_table(env, database, filename):
    ctg_connection = "{}_connection".format(env)
    catalog_connection = glueContext.extract_jdbc_conf(ctg_connection)

    return glueContext.create_dynamic_frame.from_options(
        connection_type="postgresql",
        connection_options=get_connection_option_to_read(catalog_connection, database),
    )


def get_websocket_record(env, database, filename):
    websocket_df = read_websocket_table(env, database, filename)
    websocket_df.show()
    user = get_user_and_file(filename)

    (connection_id, user_id, file_name) = get_values_from_dynamic_df(
        websocket_df, user, filename
    )

    websocket_result = "connection: {}, user: {}, file: {}".format(
        connection_id, user_id, file_name
    )
    logger.warning(websocket_result)

    return (connection_id, user_id, file_name)


def main():
    args = getResolvedOptions(sys.argv, ["ENV", "FILENAME", "BUCKET"])
    file_name = args["FILENAME"]
    bucket_name = args["BUCKET"]
    env = args["ENV"]

    file = file_name.split("{}/".format(env))[-1]
    database = "kpinetworkdb"
    if env == "demo":
        database = "demokpinetworkdb"

    start_job(env, file_name, bucket_name)

    (connection_id, user_id, file_name) = get_websocket_record(env, database, file)
    call_lambda(env, user_id, file_name, connection_id)


main()

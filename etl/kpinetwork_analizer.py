import sys
import uuid
import datetime
import re
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql import SparkSession
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import DateType

glueContext = GlueContext(SparkContext.getOrCreate())
spark = SparkSession.builder.getOrCreate()
df_schema_company = [
    "id",
    "name",
    "sector",
    "vertical",
    "inves_profile_name",
    "margin_group",
    "from_date",
    "fiscal_year",
]
df_schema_time_period = ["id", "start_at", "end_at"]
df_schema_scenario = ["id", "name", "currency", "period_id", "type", "company_id"]
df_schema_metric = [
    "id",
    "name",
    "value",
    "period_id",
    "type",
    "company_id",
    "data_type",
]
df_schema_currency = ["id", "metric_id", "currency_iso_code"]
df_schema_metric_scenario = ["id", "metric_id", "scenario_id"]
df_schema_company_location = ["id", "company_id", "country", "city", "address", "geo"]
growth_types = "Medium|Hyper|Negative|Low|High"


def save_database(env, db_table, dataframe):
    database = "kpinetworkdb"
    if env == "demo":
        database = "demokpinetworkdb"

    print("==========Save in Database===============================")
    print("env: {} database: {} db_table: {}".format(env, database, db_table))
    dynamic_frame = DynamicFrame.fromDF(dataframe, glueContext, db_table)
    glueContext.write_dynamic_frame.from_jdbc_conf(
        dynamic_frame,
        catalog_connection="{}_connection".format(env),
        connection_options={"dbtable": db_table, "database": database},
    )


def get_scenarios_limits(df_main_headers):
    scenarios = []
    for index in range(11, len(df_main_headers), 1):
        header = df_main_headers[index]
        next_header = ""
        if index < len(df_main_headers) - 1:
            next_header = df_main_headers[index + 1]
        if ":" in header:
            start = header.find(":") + 1
            scenario_name = header[start:]
            start_position = index
        if ":" in next_header or index == len(df_main_headers) - 1:
            end_position = index
            header_info = (scenario_name, start_position, end_position)
            scenarios.append(header_info)
            start_position = 0
            scenario_name = ""
    df_scenario = spark.createDataFrame(scenarios, ["name", "start", "end"])
    df_scenario.show()
    return df_scenario


def get_metrics_limits(data_collect_scenario, data_collect):
    metrics = []
    for row in data_collect_scenario:
        start_position_metric = 0
        metric_name = ""
        for index in range(row["start"], row["end"] + 1, 1):
            header = ""
            if data_collect[0][index] is not None:
                header = data_collect[0][index]
            next_header = ""
            if index < row["end"]:
                if data_collect[0][index + 1] is not None:
                    next_header = data_collect[0][index + 1]
            if ":" in header:
                start = header.find(":") + 1
                metric_name = header[start:]
                start_position_metric = index
            if ":" in next_header or index == row["end"]:
                end_position = index
                header_info = (
                    row["name"],
                    metric_name,
                    start_position_metric,
                    end_position,
                )
                metrics.append(header_info)
                metric_name = ""
    df_metrics = spark.createDataFrame(
        metrics, ["scene", "name", "start", "end"]  # add your column names here
    )
    df_metrics.show()
    return df_metrics


def get_company_information(data_collect, index):
    company = data_collect[index][0]
    sector = data_collect[index][6]
    vertical = data_collect[index][7]
    investor = data_collect[index][8]
    margin_group_target = data_collect[index][9]
    margin_group = re.findall(growth_types, margin_group_target, flags=re.IGNORECASE)
    now = datetime.datetime.utcnow()
    from_date = now.strftime("%Y-%m-%d")
    fiscal_year = now.strftime("%Y-%m-%d")
    company_id = str(uuid.uuid4())

    return (
        company_id,
        company,
        sector,
        vertical,
        investor,
        margin_group[0],
        from_date,
        fiscal_year,
    )


# TO DO implement this function when location information is available in csv file
def get_company_geo_information(data_collect, index, company_id):
    country = str(data_collect[index][2] or "")
    city = str(data_collect[index][3] or "")
    address = str(data_collect[index][4] or "")
    geo = str(data_collect[index][5] or "")
    location_id = str(uuid.uuid4())

    return location_id, company_id, country, city, address, geo


def check_time_periods_scenarios(scenarios_time_periods, scenario_name):
    time_period_id = ""
    scenario_id = ""
    create_scenario = True
    create_period = True
    if scenario_name in scenarios_time_periods:
        time_period_id = scenarios_time_periods[scenario_name]["idTimePeriod"]
        scenario_id = scenarios_time_periods[scenario_name]["idScene"]
        create_scenario = False
        create_period = False

    else:
        scenarios_time_periods.update(
            {
                scenario_name: {
                    "idTimePeriod": str(uuid.uuid4()),
                    "idScene": str(uuid.uuid4()),
                }
            }
        )
        time_period_id = scenarios_time_periods[scenario_name]["idTimePeriod"]
        scenario_id = scenarios_time_periods[scenario_name]["idScene"]
    return (
        time_period_id,
        scenario_id,
        create_scenario,
        create_period,
        scenarios_time_periods,
    )


def get_metric_value_parsed(metric_value, data_type, data_type_checked):
    if "." in metric_value:
        metric_value = float(metric_value)
        if not data_type_checked:
            data_type = "decimal"
    else:
        metric_value = int(metric_value)
        if not data_type_checked:
            data_type = "integer"
    return data_type, metric_value


def get_data_type_metric(metric_value, metric_id, currency, currency_data):
    data_type = "integer"
    data_type_checked = False
    # Check metric type
    if "$" in metric_value:
        data_type = "currency"
        currency_id = str(uuid.uuid4())
        currency_data.append((currency_id, metric_id, currency))
        data_type_checked = True
    if "%" in metric_value:
        data_type = "percentage"
        data_type_checked = True

    # Replace special characters to parse string to integer or double
    metric_value = metric_value.replace("$", "").replace("%", "")

    data_type, metric_value = get_metric_value_parsed(
        metric_value, data_type, data_type_checked
    )
    return data_type, metric_value, currency_data


def build_metric_data(
    metric_limit, data_collect, metric_index, index, metric_id, currency, currency_data
):
    metric_name = metric_limit["name"]
    # TO DO Add logic to difference between standard and custom
    metric_type = "standard"
    metric_value = data_collect[index][metric_index]
    # Check metric type
    data_type, metric_value, currency_data = get_data_type_metric(
        metric_value, metric_id, currency, currency_data
    )

    return metric_name, metric_type, metric_value, data_type, currency_data


def set_time_period_data(
    create_period, start_time, end_time, time_period_id, time_periods_data
):
    # Set time period data
    if create_period:
        time_periods_data.append((time_period_id, start_time, end_time))

    return time_periods_data


def set_scenarios_data(
    create_scenario,
    metric_limit,
    scenarios_data,
    scenario_id,
    scenario_name,
    currency,
    time_period_id,
    company_id,
):
    if create_scenario:
        scenario_type = metric_limit["scene"]
        scenarios_data.append(
            (
                scenario_id,
                scenario_name,
                currency,
                time_period_id,
                scenario_type,
                company_id,
            )
        )

    return scenarios_data


def get_scenario_metric_data(
    data_collect_metrics_limits,
    data_collect,
    previous_scenario,
    scenarios_time_periods,
    currency,
    company_id,
    index,
):
    scenarios_data = []
    metrics_data = []
    time_periods_data = []
    currency_data = []
    metric_scenario_data = []
    for metric_limit in data_collect_metrics_limits:
        if previous_scenario != metric_limit["scene"]:
            scenarios_time_periods = {}
            previous_scenario = metric_limit["scene"]

        for metric_index in range(metric_limit["start"], metric_limit["end"] + 1, 1):
            metric_scenario_id = str(uuid.uuid4())
            metric_id = str(uuid.uuid4())
            scenario_name = "{}-{}".format(
                previous_scenario, data_collect[1][metric_index]
            )
            start_time = "{}-01-01".format(data_collect[1][metric_index])
            end_time = "{}-12-31".format(data_collect[1][metric_index])
            (
                time_period_id,
                scenario_id,
                create_scenario,
                create_period,
                scenarios_time_periods,
            ) = check_time_periods_scenarios(scenarios_time_periods, scenario_name)

            # Set time period data
            time_periods_data = set_time_period_data(
                create_period, start_time, end_time, time_period_id, time_periods_data
            )

            # Set scenario data
            scenarios_data = set_scenarios_data(
                create_scenario,
                metric_limit,
                scenarios_data,
                scenario_id,
                scenario_name,
                currency,
                time_period_id,
                company_id,
            )
            # Set metric data
            (
                metric_name,
                metric_type,
                metric_value,
                data_type,
                currency_data,
            ) = build_metric_data(
                metric_limit,
                data_collect,
                metric_index,
                index,
                metric_id,
                currency,
                currency_data,
            )

            metric_scenario_data.append((metric_scenario_id, metric_id, scenario_id))

            metrics_data.append(
                (
                    metric_id,
                    metric_name,
                    metric_value,
                    time_period_id,
                    metric_type,
                    company_id,
                    data_type,
                )
            )

    return (
        scenarios_data,
        metrics_data,
        time_periods_data,
        currency_data,
        metric_scenario_data,
    )


def dataframe_cast_date_type(data_frame, columns):
    for column in columns:
        data_frame = data_frame.withColumn(column, data_frame[column].cast(DateType()))

    return data_frame


def save_dataframes(
    df_company_information,
    df_time_period_information,
    df_scenario_information,
    df_metric_information,
    df_currency_information,
    df_metric_scenario_information,
    env,
):
    print("==========Company===============================")
    df_company = spark.createDataFrame(df_company_information, df_schema_company)
    df_company = dataframe_cast_date_type(df_company, ["from_date", "fiscal_year"])
    df_company.show()
    save_database(env, "company", df_company)
    print("==========Time Period===============================")
    df_time_period = spark.createDataFrame(
        df_time_period_information, df_schema_time_period
    )
    df_time_period = dataframe_cast_date_type(df_time_period, ["start_at", "end_at"])
    df_time_period.show()
    save_database(env, "time_period", df_time_period)

    print("==========Scenarios===============================")
    df_scenario = spark.createDataFrame(df_scenario_information, df_schema_scenario)
    df_scenario.show()
    save_database(env, "financial_scenario", df_scenario)

    print("==========Metrics===============================")
    df_metrics = spark.createDataFrame(df_metric_information, df_schema_metric)

    df_metrics.show()
    save_database(env, "metric", df_metrics)

    if len(df_currency_information) > 0:
        print("==========Currency Metrics===============================")
        df_currency = spark.createDataFrame(df_currency_information, df_schema_currency)
        df_currency.show()
        save_database(env, "currency_metric", df_currency)

    print("==========Metrics-Scenarios===============================")
    df_metric_scenario = spark.createDataFrame(
        df_metric_scenario_information, df_schema_metric_scenario
    )

    df_metric_scenario.show()
    save_database(env, "scenario_metric", df_metric_scenario)


def process_dataframes(data_collect, data_collect_metrics_limits, file_dataframe, env):
    df_company_information = []
    df_time_period_information = []
    df_scenario_information = []
    df_metric_information = []
    df_currency_information = []
    df_metric_scenario_information = []
    print("=========process_dataframes========")
    for index in range(2, file_dataframe.count(), 1):
        currency = data_collect[index][1]
        company_information = get_company_information(data_collect, index)
        df_company_information.append(company_information)
        previous_scenario = ""
        scenarios_time_periods = {}
        (
            scenarios_data,
            metrics_data,
            time_periods_data,
            currency_data,
            metric_scenario_data,
        ) = get_scenario_metric_data(
            data_collect_metrics_limits,
            data_collect,
            previous_scenario,
            scenarios_time_periods,
            currency,
            company_information[0],
            index,
        )

        df_time_period_information = df_time_period_information + time_periods_data
        df_scenario_information = df_scenario_information + scenarios_data
        df_metric_information = df_metric_information + metrics_data
        df_currency_information = df_currency_information + currency_data
        df_metric_scenario_information = (
            df_metric_scenario_information + metric_scenario_data
        )

    save_dataframes(
        df_company_information,
        df_time_period_information,
        df_scenario_information,
        df_metric_information,
        df_currency_information,
        df_metric_scenario_information,
        env,
    )


def process_file(file_dataframe, env):
    df_main_headers = file_dataframe.columns
    data_collect = file_dataframe.collect()
    print("==========File Headers===============================")
    print(df_main_headers)
    df_scenarios_limits = get_scenarios_limits(df_main_headers)
    data_collect_scenarios_limits = df_scenarios_limits.collect()
    df_metrics_limits = get_metrics_limits(data_collect_scenarios_limits, data_collect)
    data_collect_metrics_limits = df_metrics_limits.collect()
    process_dataframes(data_collect, data_collect_metrics_limits, file_dataframe, env)


def main():
    args = getResolvedOptions(sys.argv, ["ENV", "FILENAME", "BUCKET"])
    file_name = args["FILENAME"]
    bucket_name = args["BUCKET"]
    env = args["ENV"]
    print("Bucket Name", bucket_name)
    print("File Name", file_name)
    print("env", env)
    input_file_path = "s3://{}/{}".format(bucket_name, file_name)
    print("Input File Path : ", input_file_path)

    file_dataframe = (
        spark.read.format("csv")
        .option("header", "true")
        .option("delimiter", ",")
        .load(input_file_path)
    )
    process_file(file_dataframe, env)


main()

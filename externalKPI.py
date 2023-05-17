import json
import datetime
from datetime import date
import pandas as pd
from pathlib import Path
import modelop.schema.infer as infer
import logging


logger = logging.getLogger(__name__)

LABEL_COLUMN = None
SCORE_COLUMN = None
JOB = {}

#
# This is the model initialization function.  This function will be called once when the model is initially loaded.  At
# this time we can read information about the job that is resulting in this model being loaded, including the full
# job in the initialization parameter
#
# Note that in a monitor, the actual model on which the monitor is being run will be in the referenceModel parameter,
# and the monitor code itself will be in the model parameter.
#

# modelop.init
def init(init_param):

    global LABEL_COLUMN
    global SCORE_COLUMN
    global JOB
    global TODAY
    
    job_json = init_param
    JOB = json.loads(init_param["rawJson"])

    #Get today's date
    TODAY = datetime.datetime.now()
    print("Beginnging processing for today. Date= ", TODAY.strftime("%d-%b-%y"))

    #Obtain the name of the label (i.e. "actuals") column and score (i.e. predictions) columns from the schema. 
    #This will be used by the metrics function to filter the input data to the actuals/label and score data only
    if job_json is not None:
        logger.info(
            "Parameter 'job_json' is present and will be used to extract "
            "'label_column' and 'score_column'."
        )

        input_schema_definition = infer.extract_input_schema(job_json)
        monitoring_parameters = infer.set_monitoring_parameters(
            schema_json=input_schema_definition, check_schema=True
        )
        LABEL_COLUMN = monitoring_parameters['label_column']
        SCORE_COLUMN = monitoring_parameters['score_column']
    else:
        logger.info(
            "Parameter 'job_json' it not present, attempting to use "
            "'label_column' and 'score_column' instead."
        )
        if LABEL_COLUMN is None:
            missing_args_error = (
                "Parameter 'job_json' is not present,"
                " but 'label_column'. "
                "'label_column' input parameter is"
                " required if 'job_json' is not provided."
            )
            logger.error(missing_args_error)
            raise Exception(missing_args_error)
       
        
#
# This method is the modelops metrics method.  This is always called with a pandas dataframe that is arraylike, and
# contains individual rows represented in a dataframe format that is representative of all of the data that comes in
# as the results of the first input asset on the job.  This method will not be invoked until all data has been read
# from that input asset.
#
# For this example, we simply echo back the first row of that data as a json object.  This is useful for things like
# reading externally generated metrics from an SQL database or an S3 file and having them interpreted as a model test
# result for the association of these results with a model snapshot.
#
# data - The input data of the first input asset of the job, as a pandas dataframe
#

# modelop.metrics
def metrics(data: pd.DataFrame):

    ##### Retrieving threshold for the day from KPI file
    try:
        print('Attempting to extract the KPI threshold file information from the Job details.')
        
        # Look for the config file in the additionalAssets section of the Job object
        additional_assets = JOB.get('additionalAssets', [])
        
        #Assume that the first asset in the additionalAssets section is the config file. 
        #Grab the filename, which will be used to read the values in the getCurrentDayKPI function
        configFileName = "./" + additional_assets[0]['filename']
        print(f'Extracted KPI File Name: {configFileName}')

        #Call the getCurrentDayKPI function, passing in the config file name from the Job
        #Return the current day's metric
        currentMetric = None
        currentMetric = getCurrentDayKPI(configFileName)
        print("CurrentDayKPI is :",currentMetric)
        
    except Exception as e:
        print('Unable to extract the threshold from the job information.')
        print(e)
    
    
    #Filter the data to today's data only
    todayDataDF = data[(pd.to_datetime(data['present_employment_since']) == TODAY.strftime("%d-%b-%y"))]
    print("Number of Production records for today: ", len(todayDataDF))
    
    #Calculate the conversion rate for the day
    conversationRate = len(todayDataDF[todayDataDF[LABEL_COLUMN]==1])/len(todayDataDF)
    
    yield {"currentDay_KPI" : currentMetric, "currentDay_ConversionRate" : conversationRate}


def getCurrentDayKPI(configFileName):

    #Read the config file, assuming that it is a CSV
    kpiDF = pd.read_csv(configFileName)

    #Find the KPI thresholds for today's date
    resultRecord = kpiDF[(pd.to_datetime(kpiDF['POLEFFDATE_M']) == TODAY.strftime("%d-%b-%y"))]

    if resultRecord is not None:
        #In case there are more than one KPI records returned, take the average of all of them
        kpiThreshold = resultRecord['Modeled_Policy_Renewal'].mean()
    else:
        kpiThreshold = None
        print("no matching dates")
    
    return kpiThreshold
    
#
# This main method is utilized to simulate what the engine will do when calling the above metrics function.  It takes
# the json/csv formatted data, and converts it to a pandas dataframe, then passes this into the metrics function for
# processing.  This is a good way to develop your models to be conformant with the engine in that you can run this
# locally first and ensure the python is behaving correctly before deploying on a ModelOp engine.
#
def main():
    raw_json = Path('GC_job.json').read_text()
    init_param = {'rawJson': raw_json}
    init(init_param)

    df = pd.read_json('df_sample_scored.json', lines=True)
    print(next(metrics(df)))


if __name__ == '__main__':
	main()

import json
from datetime import datetime
import pandas as pd
from pathlib import Path
import modelop.schema.infer as infer
import logging


logger = logging.getLogger(__name__)

LABEL_COLUMN = None
SCORE_COLUMN = None

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

    job_json = init_param
    job = json.loads(init_param["rawJson"])

    if job_json is not None:
        logger.info(
            "Parameter 'job_json' is present and will be used to extract "
            "'label_column' and 'score_column'."
        )
        ##### Retrieving jobParameters
        try:
            print('Attempting to extract the KPI threshold file from jobParameters.')
            additional_assets = job.get('additionalAssets', [])
            print(f'Extracted Asset Information: {additional_assets[0]}')
        except Exception as e:
            print('Unable to extract the BUCKET_COLUMN from jobParameters.')
            print(e)
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
    df2 = len(data[data[LABEL_COLUMN]==1])
    yield df2


#
# This main method is utilized to simulate what the engine will do when calling the above metrics function.  It takes
# the json formatted data, and converts it to a pandas dataframe, then passes this into the metrics function for
# processing.  This is a good way to develop your models to be conformant with the engine in that you can run this
# locally first and ensure the python is behaving correctly before deploying on a ModelOp engine.
#
def main():
    raw_json = Path('GC_job.json').read_text()
    init_param = {'rawJson': raw_json}
    init(init_param)

#     data_dict = []
#     with open('df_sample_scored.json','r') as f:
#         for line in f:
#             data_dict.append(json.loads(line))
#     df = pd.DataFrame.from_dict([data_dict])
    df = pd.read_json('df_sample_scored.json', lines=True)
    print(next(metrics(df)))


if __name__ == '__main__':
	main()

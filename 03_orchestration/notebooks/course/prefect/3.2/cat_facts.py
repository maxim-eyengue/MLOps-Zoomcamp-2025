# Necessary import
import httpx
from prefect import flow, task


# Retry the task for times waiting between retries and sharing print statements
@task(retries = 4, retry_delay_seconds = 0.1, log_prints = True)
def fetch_cat_fact():
    # Access an endpoint
    cat_fact = httpx.get("https://f3-vyx5c2hfpq-ue.a.run.app/")
    # An endpoint that is designed to fail sporadically
    if cat_fact.status_code >= 400:
        raise Exception() # raise exception if failure
    print(cat_fact.text) # print the  text of the failed request

# Define the flow
@flow
def fetch():
    fetch_cat_fact() # only one task in our flow


# If the scipt is run
if __name__ == "__main__":
    fetch() # launch the flow
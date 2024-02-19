# pulsarTriageTools
Tools used for enhancing Pulsar Triage

# URLs
https://us-east1-bobolopocus.cloudfunctions.net/triage

## Google Cloud Initialization
Use `gcloud init` to login to GCP. For this current setup, we are using the `bobolopocus` project.

## Deploying
Each function has its own deploy
```gcloud functions deploy triage --runtime python310 --trigger-http --allow-unauthenticated --entry-point=triage --gen2 --region us-east1 --env-vars-file .env.yaml```

## Deleting
```gcloud functions delete --region us-east1 {{def}}```
Example:
```gcloud functions delete --region us-east1 triage```

## Testing the URL
```curl https://us-east1-bobolopocus.cloudfunctions.net/triage```
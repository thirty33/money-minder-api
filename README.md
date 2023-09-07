# serverless-template-2023

- dependencies

1 - node: 18.17.0 (Uses nvm: https://github.com/nvm-sh/nvm) as node version manager.
2 - java latest version: https://www.oracle.com/java/technologies/downloads/
3 - python latest version: https://www.python.org/downloads/
4 - aws cli: https://docs.aws.amazon.com/es_es/cli/latest/userguide/getting-started-install.html

Installation steps:

1 clone project
2 npm install
3 run aws configure and set IAM credentials
4 to run lambdas locally: create .env files and set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY variables, then run sls offline start
5 to deploy to aws: comment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in the .env file and run: sls deploy


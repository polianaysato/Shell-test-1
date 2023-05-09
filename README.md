# options-present-value

options-present-value is a Python REST API that returns the present value of CALL and PUT options.

## endpoint 

# For uploading your spreadsheet with market data, you can use the endpoint below in Postman
PUT: https://n4sj6cm9q7.execute-api.us-east-1.amazonaws.com/Dev/shell-test-lambda/<your file name>

# For the upload, we need to change the body to binary
![PUT Postman](assets/put.png)

# After you upload your market data spreadsheet, you can call this POST API 
POST: https://n1r7e06ve8.execute-api.eu-west-2.amazonaws.com/Dev/

# You can pass your json body as in the image
![POST Postman](assets/post.png)

## Usage

```python

# build your Docker image with the command below
docker build -t <docker image name> .   

# run the command below to authenticate the Docker CLI to your Amazon ECR registry
aws ecr get-login-password --region <your region> | docker login --username AWS --password-stdin <your AWS account id>.dkr.ecr.<your region>.amazonaws.com

# Create a repository in Amazon ECR using the below command
aws ecr create-repository --repository-name <repository name> --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

# run the below command to tag your local image into your Amazon ECR repository as the latest version.
docker tag <your docker image name>:latest <your AWS account id>.dkr.ecr.<your region>.amazonaws.com/<your ECR repository>:latest
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
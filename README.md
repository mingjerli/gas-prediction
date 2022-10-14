# gas-prediction

How to run the app locally.

```
uvicorn  app:app --reload
```

I've followed this [post](https://dev.to/nick_langat/how-to-deploy-a-fastapi-app-to-aws-ec2-server-46d4) to set it up on EC2.
Need to change the file path in `gunicorn.service`.

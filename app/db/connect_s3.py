from fastapi import HTTPException
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid, os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_BUCKET_NAME ='kibwa07'
PREFIX = 'pdf/'

# boto3 clent
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

async def uploadFileToS3(file):
    try : 
        fileExtension = file.filename.split('.')[-1]
        uniqueFileName = f"{uuid.uuid4()}.{fileExtension}"
        fileContent = await file.read()
        
        filePath = PREFIX + uniqueFileName
        
        s3.put_object(
            Bucket=AWS_BUCKET_NAME,
            Body=fileContent,
            Key=filePath,
            ContentType='application/pdf'
        )
        
                # Pre-signed URL 생성 (유효기간: 1시간)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': AWS_BUCKET_NAME,
                'Key': filePath
            },
            ExpiresIn=3600
        )
        
        return {"uuid": uniqueFileName.split('.')[0], "file_url": presigned_url}
    
    
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="AWS credentials not available.")
    except PartialCredentialsError:
        raise HTTPException(status_code=400, detail="Incomplete AWS credentials provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
        
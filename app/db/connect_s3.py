from fastapi import HTTPException
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid, os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
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
        # presigned_url = s3.generate_presigned_url(
        #     'get_object',
        #     Params={
        #         'Bucket': AWS_BUCKET_NAME,
        #         'Key': filePath
        #     },
        #     ExpiresIn=3600
        # )
        
        # 지속적인 URL 생성
        fileUrl = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filePath}"
        
        return {"uuid": uniqueFileName.split('.')[0], "file_url": fileUrl, "key": filePath}
    
    
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="AWS credentials not available.")
    except PartialCredentialsError:
        raise HTTPException(status_code=400, detail="Incomplete AWS credentials provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
async def listPdfs():
    try:
        response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix=PREFIX)
        if 'Contents' not in response:
            return []

        # PDF 파일만 필터링하고 LastModified를 기준으로 정렬
        pdf_objects = sorted(
            [obj for obj in response['Contents'] if obj['Key'].endswith('.pdf')],
            key=lambda x: x['LastModified'],
            reverse=True  # 최신 순으로 정렬
        )

        # 최근 10개만 선택
        recent_pdfs = pdf_objects[:10]

        pdf_files = []
        for obj in recent_pdfs:
            # uploadFileToS3 함수에서 생성한 것과 동일한 방식으로 URL 생성
            file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
            pdf_files.append({
                'key': obj['Key'],
                'fileUrl': file_url,
                'lastModified': obj['LastModified'].isoformat()  # ISO 형식의 문자열로 변환
            })

        return pdf_files
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="AWS credentials not available.")
    except PartialCredentialsError:
        raise HTTPException(status_code=400, detail="Incomplete AWS credentials provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
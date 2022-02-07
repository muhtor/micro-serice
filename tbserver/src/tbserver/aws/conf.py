import datetime

AWS_GROUP_NAME = "GoBazar_group"
AWS_USERNAME = "ikudrat"
AWS_ACCESS_KEY_ID = "AKIA53OYWPFJ4QW3JPVZ"
AWS_SECRET_ACCESS_KEY = "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"

AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = 'tbserver.aws.utils.MediaRootS3BotoStorage'
# STATICFILES_STORAGE = 'tbserver.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'tezbor'
S3DIRECT_REGION = 'ap-south-1'
S3_URL = '//{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
MEDIA_URL = '//{}.s3.amazonaws.com/media/'.format(AWS_STORAGE_BUCKET_NAME)
MEDIA_ROOT = MEDIA_URL
AWS_DEFAULT_ACL = "public-read"
# STATIC_URL = S3_URL + 'static/'
# ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}

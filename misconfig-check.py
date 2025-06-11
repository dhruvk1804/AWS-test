import boto3

def check_s3_misconfigs():
    print("\n🔎 Checking S3 Buckets...")
    s3 = boto3.client('s3')
    try:
        buckets = s3.list_buckets()['Buckets']
        for b in buckets:
            bucket_name = b['Name']
            print(f"--- Bucket: {bucket_name} ---")

            # Public access check
            acl = s3.get_bucket_acl(Bucket=bucket_name)
            for grant in acl['Grants']:
                if 'AllUsers' in grant['Grantee'].get('URI', ''):
                    print(f"⚠️ Bucket is publicly accessible: {bucket_name}")
                    break

            # Logging check
            logging = s3.get_bucket_logging(Bucket=bucket_name)
            if 'LoggingEnabled' not in logging:
                print(f"⚠️ Logging is disabled: {bucket_name}")

            # Versioning check
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)
            if versioning.get('Status') != 'Enabled':
                print(f"⚠️ Versioning is disabled: {bucket_name}")
    except Exception as e:
        print(f"Error checking S3: {e}")

def check_rds_misconfigs():
    print("\n🔎 Checking RDS Instances...")
    rds = boto3.client('rds')
    try:
        dbs = rds.describe_db_instances()['DBInstances']
        for db in dbs:
            db_id = db['DBInstanceIdentifier']
            print(f"--- RDS Instance: {db_id} ---")

            if db['PubliclyAccessible']:
                print(f"⚠️ RDS is publicly accessible: {db_id}")

            if not db.get('DeletionProtection', False):
                print(f"⚠️ Deletion protection is disabled: {db_id}")

            if db.get('BackupRetentionPeriod', 0) == 0:
                print(f"⚠️ Backup is disabled: {db_id}")
    except Exception as e:
        print(f"Error checking RDS: {e}")

def check_security_groups():
    print("\n🔎 Checking Security Groups...")
    ec2 = boto3.client('ec2')
    try:
        sgs = ec2.describe_security_groups()['SecurityGroups']
        for sg in sgs:
            sg_id = sg['GroupId']
            sg_name = sg.get('GroupName', '')
            print(f"--- Security Group: {sg_id} ({sg_name}) ---")

            for perm in sg.get('IpPermissions', []):
                from_port = perm.get('FromPort')
                to_port = perm.get('ToPort')
                ip_ranges = perm.get('IpRanges', [])

                for ip in ip_ranges:
                    cidr = ip.get('CidrIp')
                    if cidr == '0.0.0.0/0':  # Public access
                        if from_port == 22:
                            print(f"⚠️ SSH (port 22) open to the public in SG: {sg_id}")
                        if from_port == 27017:
                            print(f"⚠️ MongoDB (port 27017) open to the public in SG: {sg_id}")
    except Exception as e:
        print(f"Error checking security groups: {e}")

# ---------- MAIN ----------
if __name__ == "__main__":
    check_s3_misconfigs()
    check_rds_misconfigs()
    check_security_groups()

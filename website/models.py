# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Companies(models.Model):
    name = models.CharField(max_length=500, blank=True, null=True)
    domain = models.CharField(max_length=500)
    year_founded = models.IntegerField(blank=True, null=True)
    industry = models.CharField(max_length=500, blank=True, null=True)
    size_range = models.CharField(max_length=45, blank=True, null=True)
    country = models.CharField(max_length=45, blank=True, null=True)
    linkedin_url = models.CharField(unique=True, max_length=500, blank=True, null=True)
    current_employee_est = models.IntegerField(blank=True, null=True)
    total_employee_est = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'companies'

class Jd(models.Model):
    crawl_timestamp = models.CharField(max_length=100)
    url = models.CharField(unique=True, max_length=600, blank=True, null=True)
    job_title = models.CharField(max_length=500)
    category = models.CharField(max_length=45, blank=True, null=True)
    company_name = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=45, blank=True, null=True)
    state = models.CharField(max_length=45, blank=True, null=True)
    country = models.CharField(max_length=45, blank=True, null=True)
    post_date = models.CharField(max_length=45, blank=True, null=True)
    job_description = models.TextField()
    job_type = models.CharField(max_length=45, blank=True, null=True)
    job_board = models.CharField(max_length=45, blank=True, null=True)
    sector = models.CharField(max_length=45, blank=True, null=True)
    html_job_description = models.TextField(blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    skill = models.TextField(blank=True, null=True)
    cleaned_jd = models.TextField(blank=True, null=True)
    domain_minik = models.CharField(max_length=50, blank=True, null=True)
    domain_lr = models.CharField(max_length=50, blank=True, null=True)
    clean_post_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jd'

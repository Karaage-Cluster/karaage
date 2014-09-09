# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', models.CharField(unique=True, max_length=255)),
                ('email', models.EmailField(max_length=75, null=True, db_index=True)),
                ('short_name', models.CharField(max_length=30)),
                ('full_name', models.CharField(max_length=60)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('saml_id', models.CharField(max_length=200, unique=True, null=True, editable=False, blank=True)),
                ('position', models.CharField(max_length=200, null=True, blank=True)),
                ('telephone', models.CharField(max_length=200, null=True, blank=True)),
                ('mobile', models.CharField(max_length=200, null=True, blank=True)),
                ('department', models.CharField(max_length=200, null=True, blank=True)),
                ('supervisor', models.CharField(max_length=100, null=True, blank=True)),
                ('title', models.CharField(blank=True, max_length=10, null=True, choices=[('', ''), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Miss', 'Miss'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof'), ('A/Prof', 'A/Prof')])),
                ('address', models.CharField(max_length=200, null=True, blank=True)),
                ('city', models.CharField(max_length=100, null=True, blank=True)),
                ('postcode', models.CharField(max_length=8, null=True, blank=True)),
                ('state', models.CharField(blank=True, max_length=4, null=True, choices=[('', '--------'), ('ACT', 'ACT'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')])),
                ('country', models.CharField(blank=True, max_length=2, null=True, choices=[('AU', 'Australia'), ('NZ', 'New Zealand'), ('GB', 'United Kingdom'), ('DE', 'Germany'), ('US', 'United States'), ('', '--------------------------------------'), ('AD', 'Andorra'), ('AE', 'United Arab Emirates'), ('AF', 'Afghanistan'), ('AG', 'Antigua and Barbuda'), ('AI', 'Anguilla'), ('AL', 'Albania'), ('AM', 'Armenia'), ('AN', 'Netherlands Antilles'), ('AO', 'Angola'), ('AQ', 'Antarctica'), ('AR', 'Argentina'), ('AS', 'American Samoa'), ('AT', 'Austria'), ('AW', 'Aruba'), ('AX', 'Aland Islands'), ('AZ', 'Azerbaijan'), ('BA', 'Bosnia and Herzegovina'), ('BB', 'Barbados'), ('BD', 'Bangladesh'), ('BE', 'Belgium'), ('BF', 'Burkina Faso'), ('BG', 'Bulgaria'), ('BH', 'Bahrain'), ('BI', 'Burundi'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BN', 'Brunei Darussalam'), ('BO', 'Bolivia'), ('BR', 'Brazil'), ('BS', 'Bahamas'), ('BT', 'Bhutan'), ('BV', 'Bouvet Island'), ('BW', 'Botswana'), ('BY', 'Belarus'), ('BZ', 'Belize'), ('CA', 'Canada'), ('CC', 'Cocos (Keeling) Islands'), ('CD', 'Congo'), ('CF', 'Central African Republic'), ('CG', 'Congo'), ('CH', 'Switzerland'), ('CI', "Cote d'Ivoire"), ('CK', 'Cook Islands'), ('CL', 'Chile'), ('CM', 'Cameroon'), ('CN', 'China'), ('CO', 'Colombia'), ('CR', 'Costa Rica'), ('CU', 'Cuba'), ('CV', 'Cape Verde'), ('CX', 'Christmas Island'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DJ', 'Djibouti'), ('DK', 'Denmark'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('DZ', 'Algeria'), ('EC', 'Ecuador'), ('EE', 'Estonia'), ('EG', 'Egypt'), ('EH', 'Western Sahara'), ('ER', 'Eritrea'), ('ES', 'Spain'), ('ET', 'Ethiopia'), ('FI', 'Finland'), ('FJ', 'Fiji'), ('FK', 'Falkland Islands'), ('FM', 'Micronesia'), ('FO', 'Faroe Islands'), ('FR', 'France'), ('GA', 'Gabon'), ('GD', 'Grenada'), ('GE', 'Georgia'), ('GF', 'French Guiana'), ('GG', 'Guernsey'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GL', 'Greenland'), ('GM', 'Gambia'), ('GN', 'Guinea'), ('GP', 'Guadeloupe'), ('GQ', 'Equatorial Guinea'), ('GR', 'Greece'), ('GS', 'South Georgia and the South Sandwich Islands'), ('GT', 'Guatemala'), ('GU', 'Guam'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HK', 'Hong Kong'), ('HM', 'Heard Island and McDonald Islands'), ('HN', 'Honduras'), ('HR', 'Croatia'), ('HT', 'Haiti'), ('HU', 'Hungary'), ('ID', 'Indonesia'), ('IE', 'Ireland'), ('IL', 'Israel'), ('IM', 'Isle of Man'), ('IN', 'India'), ('IO', 'British Indian Ocean Territory'), ('IQ', 'Iraq'), ('IR', 'Iran'), ('IS', 'Iceland'), ('IT', 'Italy'), ('JE', 'Jersey'), ('JM', 'Jamaica'), ('JO', 'Jordan'), ('JP', 'Japan'), ('KE', 'Kenya'), ('KG', 'Kyrgyzstan'), ('KH', 'Cambodia'), ('KI', 'Kiribati'), ('KM', 'Comoros'), ('KN', 'Saint Kitts and Nevis'), ('KP', 'Korea'), ('KR', 'Korea'), ('KW', 'Kuwait'), ('KY', 'Cayman Islands'), ('KZ', 'Kazakhstan'), ('LA', "Lao People's Democratic Republic"), ('LB', 'Lebanon'), ('LC', 'Saint Lucia'), ('LI', 'Liechtenstein'), ('LK', 'Sri Lanka'), ('LR', 'Liberia'), ('LS', 'Lesotho'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('LV', 'Latvia'), ('LY', 'Libyan Arab Jamahiriya'), ('MA', 'Morocco'), ('MC', 'Monaco'), ('MD', 'Moldova'), ('ME', 'Montenegro'), ('MG', 'Madagascar'), ('MH', 'Marshall Islands'), ('MK', 'Macedonia'), ('ML', 'Mali'), ('MM', 'Myanmar'), ('MN', 'Mongolia'), ('MO', 'Macao'), ('MP', 'Northern Mariana Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MS', 'Montserrat'), ('MT', 'Malta'), ('MU', 'Mauritius'), ('MV', 'Maldives'), ('MW', 'Malawi'), ('MX', 'Mexico'), ('MY', 'Malaysia'), ('MZ', 'Mozambique'), ('NA', 'Namibia'), ('NC', 'New Caledonia'), ('NE', 'Niger'), ('NF', 'Norfolk Island'), ('NG', 'Nigeria'), ('NI', 'Nicaragua'), ('NL', 'Netherlands'), ('NO', 'Norway'), ('NP', 'Nepal'), ('NR', 'Nauru'), ('NU', 'Niue'), ('OM', 'Oman'), ('PA', 'Panama'), ('PE', 'Peru'), ('PF', 'French Polynesia'), ('PG', 'Papua New Guinea'), ('PH', 'Philippines'), ('PK', 'Pakistan'), ('PL', 'Poland'), ('PM', 'Saint Pierre and Miquelon'), ('PN', 'Pitcairn'), ('PR', 'Puerto Rico'), ('PS', 'Palestinian Territory'), ('PT', 'Portugal'), ('PW', 'Palau'), ('PY', 'Paraguay'), ('QA', 'Qatar'), ('RE', 'Reunion'), ('RO', 'Romania'), ('RS', 'Serbia'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('SA', 'Saudi Arabia'), ('SB', 'Solomon Islands'), ('SC', 'Seychelles'), ('SD', 'Sudan'), ('SE', 'Sweden'), ('SG', 'Singapore'), ('SH', 'Saint Helena'), ('SI', 'Slovenia'), ('SJ', 'Svalbard and Jan Mayen'), ('SK', 'Slovakia'), ('SL', 'Sierra Leone'), ('SM', 'San Marino'), ('SN', 'Senegal'), ('SO', 'Somalia'), ('SR', 'Suriname'), ('ST', 'Sao Tome and Principe'), ('SV', 'El Salvador'), ('SY', 'Syrian Arab Republic'), ('SZ', 'Swaziland'), ('TC', 'Turks and Caicos Islands'), ('TD', 'Chad'), ('TF', 'French Southern Territories'), ('TG', 'Togo'), ('TH', 'Thailand'), ('TJ', 'Tajikistan'), ('TK', 'Tokelau'), ('TL', 'Timor-Leste'), ('TM', 'Turkmenistan'), ('TN', 'Tunisia'), ('TO', 'Tonga'), ('TR', 'Turkey'), ('TT', 'Trinidad and Tobago'), ('TV', 'Tuvalu'), ('TW', 'Taiwan'), ('TZ', 'Tanzania'), ('UA', 'Ukraine'), ('UG', 'Uganda'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VA', 'Vatican City'), ('VC', 'Saint Vincent and the Grenadines'), ('VE', 'Venezuela'), ('VG', 'Virgin Islands (British)'), ('VI', 'Virgin Islands (US)'), ('VN', 'Viet Nam'), ('VU', 'Vanuatu'), ('WF', 'Wallis and Futuna'), ('WS', 'Samoa'), ('YE', 'Yemen'), ('YT', 'Mayotte'), ('ZA', 'South Africa'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')])),
                ('website', models.URLField(null=True, blank=True)),
                ('fax', models.CharField(max_length=50, null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('date_approved', models.DateField(null=True, blank=True)),
                ('date_deleted', models.DateField(null=True, blank=True)),
                ('last_usage', models.DateField(null=True, blank=True)),
                ('expires', models.DateField(null=True, blank=True)),
                ('is_systemuser', models.BooleanField(default=False)),
                ('login_enabled', models.BooleanField(default=True)),
                ('legacy_ldap_password', models.CharField(max_length=128, null=True, blank=True)),
                ('approved_by', models.ForeignKey(related_name='user_approver', blank=True, to='karaage.Person', null=True)),
                ('deleted_by', models.ForeignKey(related_name='user_deletor', blank=True, to='karaage.Person', null=True)),
            ],
            options={
                'ordering': ['full_name', 'short_name'],
                'db_table': 'person',
                'verbose_name_plural': 'people',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=255)),
                ('foreign_id', models.CharField(help_text='The foreign identifier from the datastore.', max_length=255, unique=True, null=True)),
                ('date_created', models.DateField()),
                ('date_deleted', models.DateField(null=True, blank=True)),
                ('disk_quota', models.IntegerField(help_text='In GB', null=True, blank=True)),
                ('shell', models.CharField(max_length=50)),
                ('login_enabled', models.BooleanField(default=True)),
                ('extra_data', jsonfield.fields.JSONField(default={}, help_text='Datastore specific values should be stored in this field.')),
            ],
            options={
                'ordering': ['person'],
                'db_table': 'account',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('foreign_id', models.CharField(help_text='The foreign identifier from the datastore.', max_length=255, unique=True, null=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('extra_data', jsonfield.fields.JSONField(default={}, help_text='Datastore specific values should be stored in this field.')),
                ('members', models.ManyToManyField(related_name='groups', to='karaage.Person')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'people_group',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('saml_entityid', models.CharField(max_length=200, unique=True, null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'institute',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstituteDelegate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('send_email', models.BooleanField()),
                ('institute', models.ForeignKey(to='karaage.Institute')),
                ('person', models.ForeignKey(to='karaage.Person')),
            ],
            options={
                'db_table': 'institutedelegate',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstituteQuota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quota', models.DecimalField(max_digits=5, decimal_places=2)),
                ('cap', models.IntegerField(null=True, blank=True)),
                ('disk_quota', models.IntegerField(null=True, blank=True)),
                ('institute', models.ForeignKey(to='karaage.Institute')),
            ],
            options={
                'db_table': 'institute_quota',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_time', models.DateTimeField(auto_now_add=True, verbose_name='action time')),
                ('object_id', models.TextField(null=True, verbose_name='object id', blank=True)),
                ('object_repr', models.CharField(max_length=200, verbose_name='object repr')),
                ('action_flag', models.PositiveSmallIntegerField(verbose_name='action flag')),
                ('change_message', models.TextField(verbose_name='change message', blank=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(to='karaage.Person', null=True)),
            ],
            options={
                'ordering': ('-action_time', '-pk'),
                'db_table': 'admin_log',
                'verbose_name': 'log entry',
                'verbose_name_plural': 'log entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('name', models.CharField(unique=True, max_length=50)),
                ('no_cpus', models.IntegerField()),
                ('no_nodes', models.IntegerField()),
                ('type', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('pbs_server_host', models.CharField(max_length=50, null=True, blank=True)),
                ('mem_per_core', models.IntegerField(help_text='In GB', null=True, blank=True)),
                ('scaling_factor', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'machine',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MachineCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('datastore', models.CharField(help_text='Modifying this value on existing categories will affect accounts created under the old datastore', max_length=255, choices=[('dummy', 'dummy'), ('ldap', 'ldap')])),
            ],
            options={
                'db_table': 'machine_category',
                'verbose_name_plural': 'machine categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pid', models.CharField(unique=True, max_length=255)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(null=True, blank=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('start_date', models.DateField(default=datetime.datetime.today)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('additional_req', models.TextField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=False)),
                ('date_approved', models.DateField(null=True, editable=False, blank=True)),
                ('date_deleted', models.DateField(null=True, editable=False, blank=True)),
                ('last_usage', models.DateField(null=True, editable=False, blank=True)),
                ('approved_by', models.ForeignKey(related_name='project_approver', blank=True, editable=False, to='karaage.Person', null=True)),
                ('deleted_by', models.ForeignKey(related_name='project_deletor', blank=True, editable=False, to='karaage.Person', null=True)),
                ('group', models.ForeignKey(to='karaage.Group')),
                ('institute', models.ForeignKey(to='karaage.Institute')),
                ('leaders', models.ManyToManyField(related_name='leads', to='karaage.Person')),
            ],
            options={
                'ordering': ['pid'],
                'db_table': 'project',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectQuota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cap', models.IntegerField(null=True, blank=True)),
                ('machine_category', models.ForeignKey(to='karaage.MachineCategory')),
                ('project', models.ForeignKey(to='karaage.Project')),
            ],
            options={
                'db_table': 'project_quota',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='projectquota',
            unique_together=set([('project', 'machine_category')]),
        ),
        migrations.AddField(
            model_name='machine',
            name='category',
            field=models.ForeignKey(to='karaage.MachineCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institutequota',
            name='machine_category',
            field=models.ForeignKey(to='karaage.MachineCategory'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='institutequota',
            unique_together=set([('institute', 'machine_category')]),
        ),
        migrations.AddField(
            model_name='institute',
            name='delegates',
            field=models.ManyToManyField(related_name='delegate_for', null=True, through='karaage.InstituteDelegate', to='karaage.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institute',
            name='group',
            field=models.ForeignKey(to='karaage.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='default_project',
            field=models.ForeignKey(blank=True, to='karaage.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='machine_category',
            field=models.ForeignKey(to='karaage.MachineCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='person',
            field=models.ForeignKey(to='karaage.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='institute',
            field=models.ForeignKey(to='karaage.Institute'),
            preserve_default=True,
        ),
    ]

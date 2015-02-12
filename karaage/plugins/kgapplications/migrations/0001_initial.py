# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import karaage.common


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('email_verified', models.BooleanField(default=False, editable=False)),
                ('username', models.CharField(max_length=255, unique=True, null=True, blank=True)),
                ('title', models.CharField(blank=True, max_length=10, null=True, choices=[('', ''), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Miss', 'Miss'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof'), ('A/Prof', 'A/Prof')])),
                ('short_name', models.CharField(max_length=30)),
                ('full_name', models.CharField(max_length=60)),
                ('department', models.CharField(max_length=200, null=True, blank=True)),
                ('position', models.CharField(max_length=200, null=True, blank=True)),
                ('telephone', models.CharField(max_length=200, null=True, verbose_name='Office Telephone', blank=True)),
                ('mobile', models.CharField(max_length=200, null=True, blank=True)),
                ('supervisor', models.CharField(max_length=100, null=True, blank=True)),
                ('address', models.CharField(max_length=200, null=True, blank=True)),
                ('city', models.CharField(max_length=100, null=True, blank=True)),
                ('postcode', models.CharField(max_length=8, null=True, blank=True)),
                ('country', models.CharField(blank=True, max_length=2, null=True, choices=[('AU', 'Australia'), ('NZ', 'New Zealand'), ('GB', 'United Kingdom'), ('DE', 'Germany'), ('US', 'United States'), ('', '--------------------------------------'), ('AD', 'Andorra'), ('AE', 'United Arab Emirates'), ('AF', 'Afghanistan'), ('AG', 'Antigua and Barbuda'), ('AI', 'Anguilla'), ('AL', 'Albania'), ('AM', 'Armenia'), ('AN', 'Netherlands Antilles'), ('AO', 'Angola'), ('AQ', 'Antarctica'), ('AR', 'Argentina'), ('AS', 'American Samoa'), ('AT', 'Austria'), ('AW', 'Aruba'), ('AX', 'Aland Islands'), ('AZ', 'Azerbaijan'), ('BA', 'Bosnia and Herzegovina'), ('BB', 'Barbados'), ('BD', 'Bangladesh'), ('BE', 'Belgium'), ('BF', 'Burkina Faso'), ('BG', 'Bulgaria'), ('BH', 'Bahrain'), ('BI', 'Burundi'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BN', 'Brunei Darussalam'), ('BO', 'Bolivia'), ('BR', 'Brazil'), ('BS', 'Bahamas'), ('BT', 'Bhutan'), ('BV', 'Bouvet Island'), ('BW', 'Botswana'), ('BY', 'Belarus'), ('BZ', 'Belize'), ('CA', 'Canada'), ('CC', 'Cocos (Keeling) Islands'), ('CD', 'Congo'), ('CF', 'Central African Republic'), ('CG', 'Congo'), ('CH', 'Switzerland'), ('CI', "Cote d'Ivoire"), ('CK', 'Cook Islands'), ('CL', 'Chile'), ('CM', 'Cameroon'), ('CN', 'China'), ('CO', 'Colombia'), ('CR', 'Costa Rica'), ('CU', 'Cuba'), ('CV', 'Cape Verde'), ('CX', 'Christmas Island'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DJ', 'Djibouti'), ('DK', 'Denmark'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('DZ', 'Algeria'), ('EC', 'Ecuador'), ('EE', 'Estonia'), ('EG', 'Egypt'), ('EH', 'Western Sahara'), ('ER', 'Eritrea'), ('ES', 'Spain'), ('ET', 'Ethiopia'), ('FI', 'Finland'), ('FJ', 'Fiji'), ('FK', 'Falkland Islands'), ('FM', 'Micronesia'), ('FO', 'Faroe Islands'), ('FR', 'France'), ('GA', 'Gabon'), ('GD', 'Grenada'), ('GE', 'Georgia'), ('GF', 'French Guiana'), ('GG', 'Guernsey'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GL', 'Greenland'), ('GM', 'Gambia'), ('GN', 'Guinea'), ('GP', 'Guadeloupe'), ('GQ', 'Equatorial Guinea'), ('GR', 'Greece'), ('GS', 'South Georgia and the South Sandwich Islands'), ('GT', 'Guatemala'), ('GU', 'Guam'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HK', 'Hong Kong'), ('HM', 'Heard Island and McDonald Islands'), ('HN', 'Honduras'), ('HR', 'Croatia'), ('HT', 'Haiti'), ('HU', 'Hungary'), ('ID', 'Indonesia'), ('IE', 'Ireland'), ('IL', 'Israel'), ('IM', 'Isle of Man'), ('IN', 'India'), ('IO', 'British Indian Ocean Territory'), ('IQ', 'Iraq'), ('IR', 'Iran'), ('IS', 'Iceland'), ('IT', 'Italy'), ('JE', 'Jersey'), ('JM', 'Jamaica'), ('JO', 'Jordan'), ('JP', 'Japan'), ('KE', 'Kenya'), ('KG', 'Kyrgyzstan'), ('KH', 'Cambodia'), ('KI', 'Kiribati'), ('KM', 'Comoros'), ('KN', 'Saint Kitts and Nevis'), ('KP', 'Korea'), ('KR', 'Korea'), ('KW', 'Kuwait'), ('KY', 'Cayman Islands'), ('KZ', 'Kazakhstan'), ('LA', "Lao People's Democratic Republic"), ('LB', 'Lebanon'), ('LC', 'Saint Lucia'), ('LI', 'Liechtenstein'), ('LK', 'Sri Lanka'), ('LR', 'Liberia'), ('LS', 'Lesotho'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('LV', 'Latvia'), ('LY', 'Libyan Arab Jamahiriya'), ('MA', 'Morocco'), ('MC', 'Monaco'), ('MD', 'Moldova'), ('ME', 'Montenegro'), ('MG', 'Madagascar'), ('MH', 'Marshall Islands'), ('MK', 'Macedonia'), ('ML', 'Mali'), ('MM', 'Myanmar'), ('MN', 'Mongolia'), ('MO', 'Macao'), ('MP', 'Northern Mariana Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MS', 'Montserrat'), ('MT', 'Malta'), ('MU', 'Mauritius'), ('MV', 'Maldives'), ('MW', 'Malawi'), ('MX', 'Mexico'), ('MY', 'Malaysia'), ('MZ', 'Mozambique'), ('NA', 'Namibia'), ('NC', 'New Caledonia'), ('NE', 'Niger'), ('NF', 'Norfolk Island'), ('NG', 'Nigeria'), ('NI', 'Nicaragua'), ('NL', 'Netherlands'), ('NO', 'Norway'), ('NP', 'Nepal'), ('NR', 'Nauru'), ('NU', 'Niue'), ('OM', 'Oman'), ('PA', 'Panama'), ('PE', 'Peru'), ('PF', 'French Polynesia'), ('PG', 'Papua New Guinea'), ('PH', 'Philippines'), ('PK', 'Pakistan'), ('PL', 'Poland'), ('PM', 'Saint Pierre and Miquelon'), ('PN', 'Pitcairn'), ('PR', 'Puerto Rico'), ('PS', 'Palestinian Territory'), ('PT', 'Portugal'), ('PW', 'Palau'), ('PY', 'Paraguay'), ('QA', 'Qatar'), ('RE', 'Reunion'), ('RO', 'Romania'), ('RS', 'Serbia'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('SA', 'Saudi Arabia'), ('SB', 'Solomon Islands'), ('SC', 'Seychelles'), ('SD', 'Sudan'), ('SE', 'Sweden'), ('SG', 'Singapore'), ('SH', 'Saint Helena'), ('SI', 'Slovenia'), ('SJ', 'Svalbard and Jan Mayen'), ('SK', 'Slovakia'), ('SL', 'Sierra Leone'), ('SM', 'San Marino'), ('SN', 'Senegal'), ('SO', 'Somalia'), ('SR', 'Suriname'), ('ST', 'Sao Tome and Principe'), ('SV', 'El Salvador'), ('SY', 'Syrian Arab Republic'), ('SZ', 'Swaziland'), ('TC', 'Turks and Caicos Islands'), ('TD', 'Chad'), ('TF', 'French Southern Territories'), ('TG', 'Togo'), ('TH', 'Thailand'), ('TJ', 'Tajikistan'), ('TK', 'Tokelau'), ('TL', 'Timor-Leste'), ('TM', 'Turkmenistan'), ('TN', 'Tunisia'), ('TO', 'Tonga'), ('TR', 'Turkey'), ('TT', 'Trinidad and Tobago'), ('TV', 'Tuvalu'), ('TW', 'Taiwan'), ('TZ', 'Tanzania'), ('UA', 'Ukraine'), ('UG', 'Uganda'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VA', 'Vatican City'), ('VC', 'Saint Vincent and the Grenadines'), ('VE', 'Venezuela'), ('VG', 'Virgin Islands (British)'), ('VI', 'Virgin Islands (US)'), ('VN', 'Viet Nam'), ('VU', 'Vanuatu'), ('WF', 'Wallis and Futuna'), ('WS', 'Samoa'), ('YE', 'Yemen'), ('YT', 'Mayotte'), ('ZA', 'South Africa'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')])),
                ('fax', models.CharField(max_length=50, null=True, blank=True)),
                ('saml_id', models.CharField(max_length=200, unique=True, null=True, editable=False, blank=True)),
                ('institute', models.ForeignKey(blank=True, to='karaage.Institute', help_text='If your institute is not listed please contact accounts@example.com', null=True)),
            ],
            options={
                'db_table': 'applications_applicant',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('secret_token', models.CharField(default=karaage.common.new_random_token, unique=True, max_length=64, editable=False)),
                ('expires', models.DateTimeField(editable=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('submitted_date', models.DateTimeField(null=True, blank=True)),
                ('state', models.CharField(max_length=5)),
                ('complete_date', models.DateTimeField(null=True, editable=False, blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('header_message', models.TextField(help_text='Message displayed at top of application form for the invitee and also in invitation email', null=True, verbose_name='Message', blank=True)),
                ('_class', models.CharField(max_length=100, editable=False)),
            ],
            options={
                'db_table': 'applications_application',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectApplication',
            fields=[
                ('application_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='kgapplications.Application')),
                ('needs_account', models.BooleanField(default=True, help_text='Required if you will be working on the project yourself.', verbose_name='Do you need a personal cluster account?')),
                ('make_leader', models.BooleanField(default=False, help_text='Make this person a project leader')),
                ('name', models.CharField(max_length=200, verbose_name='Title')),
                ('description', models.TextField(null=True, blank=True)),
                ('additional_req', models.TextField(null=True, blank=True)),
                ('pid', models.CharField(max_length=50, null=True, blank=True)),
                ('institute', models.ForeignKey(blank=True, to='karaage.Institute', null=True)),
                ('machine_categories', models.ManyToManyField(to='karaage.MachineCategory', null=True, blank=True)),
                ('project', models.ForeignKey(blank=True, to='karaage.Project', null=True)),
            ],
            options={
                'db_table': 'applications_projectapplication',
            },
            bases=('kgapplications.application',),
        ),
        migrations.AddField(
            model_name='application',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, to='karaage.Person', null=True),
            preserve_default=True,
        ),
    ]

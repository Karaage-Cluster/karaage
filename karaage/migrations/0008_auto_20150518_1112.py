# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('karaage', '0007_auto_20150317_1431'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonAuditLogEntry',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('username', models.CharField(max_length=255, db_index=True)),
                ('email', models.EmailField(max_length=254, null=True, db_index=True)),
                ('short_name', models.CharField(max_length=30)),
                ('full_name', models.CharField(max_length=60)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('saml_id', models.CharField(db_index=True, max_length=200, null=True, editable=False, blank=True)),
                ('position', models.CharField(max_length=200, null=True, blank=True)),
                ('telephone', models.CharField(max_length=200, null=True, blank=True)),
                ('mobile', models.CharField(max_length=200, null=True, blank=True)),
                ('department', models.CharField(max_length=200, null=True, blank=True)),
                ('supervisor', models.CharField(max_length=100, null=True, blank=True)),
                ('title', models.CharField(blank=True, max_length=10, null=True, choices=[(b'', b''), (b'Mr', b'Mr'), (b'Mrs', b'Mrs'), (b'Miss', b'Miss'), (b'Ms', b'Ms'), (b'Dr', b'Dr'), (b'Prof', b'Prof'), (b'A/Prof', b'A/Prof')])),
                ('address', models.CharField(max_length=200, null=True, blank=True)),
                ('city', models.CharField(max_length=100, null=True, blank=True)),
                ('postcode', models.CharField(max_length=8, null=True, blank=True)),
                ('state', models.CharField(blank=True, max_length=4, null=True, choices=[(b'', b'--------'), (b'ACT', b'ACT'), (b'NSW', b'New South Wales'), (b'NT', b'Northern Territory'), (b'QLD', b'Queensland'), (b'SA', b'South Australia'), (b'TAS', b'Tasmania'), (b'VIC', b'Victoria'), (b'WA', b'Western Australia')])),
                ('country', models.CharField(blank=True, max_length=2, null=True, choices=[(b'AU', b'Australia'), (b'NZ', b'New Zealand'), (b'GB', b'United Kingdom'), (b'DE', b'Germany'), (b'US', b'United States'), (b'', b'--------------------------------------'), (b'AD', b'Andorra'), (b'AE', b'United Arab Emirates'), (b'AF', b'Afghanistan'), (b'AG', b'Antigua and Barbuda'), (b'AI', b'Anguilla'), (b'AL', b'Albania'), (b'AM', b'Armenia'), (b'AN', b'Netherlands Antilles'), (b'AO', b'Angola'), (b'AQ', b'Antarctica'), (b'AR', b'Argentina'), (b'AS', b'American Samoa'), (b'AT', b'Austria'), (b'AW', b'Aruba'), (b'AX', b'Aland Islands'), (b'AZ', b'Azerbaijan'), (b'BA', b'Bosnia and Herzegovina'), (b'BB', b'Barbados'), (b'BD', b'Bangladesh'), (b'BE', b'Belgium'), (b'BF', b'Burkina Faso'), (b'BG', b'Bulgaria'), (b'BH', b'Bahrain'), (b'BI', b'Burundi'), (b'BJ', b'Benin'), (b'BM', b'Bermuda'), (b'BN', b'Brunei Darussalam'), (b'BO', b'Bolivia'), (b'BR', b'Brazil'), (b'BS', b'Bahamas'), (b'BT', b'Bhutan'), (b'BV', b'Bouvet Island'), (b'BW', b'Botswana'), (b'BY', b'Belarus'), (b'BZ', b'Belize'), (b'CA', b'Canada'), (b'CC', b'Cocos (Keeling) Islands'), (b'CD', b'Congo'), (b'CF', b'Central African Republic'), (b'CG', b'Congo'), (b'CH', b'Switzerland'), (b'CI', b"Cote d'Ivoire"), (b'CK', b'Cook Islands'), (b'CL', b'Chile'), (b'CM', b'Cameroon'), (b'CN', b'China'), (b'CO', b'Colombia'), (b'CR', b'Costa Rica'), (b'CU', b'Cuba'), (b'CV', b'Cape Verde'), (b'CX', b'Christmas Island'), (b'CY', b'Cyprus'), (b'CZ', b'Czech Republic'), (b'DJ', b'Djibouti'), (b'DK', b'Denmark'), (b'DM', b'Dominica'), (b'DO', b'Dominican Republic'), (b'DZ', b'Algeria'), (b'EC', b'Ecuador'), (b'EE', b'Estonia'), (b'EG', b'Egypt'), (b'EH', b'Western Sahara'), (b'ER', b'Eritrea'), (b'ES', b'Spain'), (b'ET', b'Ethiopia'), (b'FI', b'Finland'), (b'FJ', b'Fiji'), (b'FK', b'Falkland Islands'), (b'FM', b'Micronesia'), (b'FO', b'Faroe Islands'), (b'FR', b'France'), (b'GA', b'Gabon'), (b'GD', b'Grenada'), (b'GE', b'Georgia'), (b'GF', b'French Guiana'), (b'GG', b'Guernsey'), (b'GH', b'Ghana'), (b'GI', b'Gibraltar'), (b'GL', b'Greenland'), (b'GM', b'Gambia'), (b'GN', b'Guinea'), (b'GP', b'Guadeloupe'), (b'GQ', b'Equatorial Guinea'), (b'GR', b'Greece'), (b'GS', b'South Georgia and the South Sandwich Islands'), (b'GT', b'Guatemala'), (b'GU', b'Guam'), (b'GW', b'Guinea-Bissau'), (b'GY', b'Guyana'), (b'HK', b'Hong Kong'), (b'HM', b'Heard Island and McDonald Islands'), (b'HN', b'Honduras'), (b'HR', b'Croatia'), (b'HT', b'Haiti'), (b'HU', b'Hungary'), (b'ID', b'Indonesia'), (b'IE', b'Ireland'), (b'IL', b'Israel'), (b'IM', b'Isle of Man'), (b'IN', b'India'), (b'IO', b'British Indian Ocean Territory'), (b'IQ', b'Iraq'), (b'IR', b'Iran'), (b'IS', b'Iceland'), (b'IT', b'Italy'), (b'JE', b'Jersey'), (b'JM', b'Jamaica'), (b'JO', b'Jordan'), (b'JP', b'Japan'), (b'KE', b'Kenya'), (b'KG', b'Kyrgyzstan'), (b'KH', b'Cambodia'), (b'KI', b'Kiribati'), (b'KM', b'Comoros'), (b'KN', b'Saint Kitts and Nevis'), (b'KP', b'Korea'), (b'KR', b'Korea'), (b'KW', b'Kuwait'), (b'KY', b'Cayman Islands'), (b'KZ', b'Kazakhstan'), (b'LA', b"Lao People's Democratic Republic"), (b'LB', b'Lebanon'), (b'LC', b'Saint Lucia'), (b'LI', b'Liechtenstein'), (b'LK', b'Sri Lanka'), (b'LR', b'Liberia'), (b'LS', b'Lesotho'), (b'LT', b'Lithuania'), (b'LU', b'Luxembourg'), (b'LV', b'Latvia'), (b'LY', b'Libyan Arab Jamahiriya'), (b'MA', b'Morocco'), (b'MC', b'Monaco'), (b'MD', b'Moldova'), (b'ME', b'Montenegro'), (b'MG', b'Madagascar'), (b'MH', b'Marshall Islands'), (b'MK', b'Macedonia'), (b'ML', b'Mali'), (b'MM', b'Myanmar'), (b'MN', b'Mongolia'), (b'MO', b'Macao'), (b'MP', b'Northern Mariana Islands'), (b'MQ', b'Martinique'), (b'MR', b'Mauritania'), (b'MS', b'Montserrat'), (b'MT', b'Malta'), (b'MU', b'Mauritius'), (b'MV', b'Maldives'), (b'MW', b'Malawi'), (b'MX', b'Mexico'), (b'MY', b'Malaysia'), (b'MZ', b'Mozambique'), (b'NA', b'Namibia'), (b'NC', b'New Caledonia'), (b'NE', b'Niger'), (b'NF', b'Norfolk Island'), (b'NG', b'Nigeria'), (b'NI', b'Nicaragua'), (b'NL', b'Netherlands'), (b'NO', b'Norway'), (b'NP', b'Nepal'), (b'NR', b'Nauru'), (b'NU', b'Niue'), (b'OM', b'Oman'), (b'PA', b'Panama'), (b'PE', b'Peru'), (b'PF', b'French Polynesia'), (b'PG', b'Papua New Guinea'), (b'PH', b'Philippines'), (b'PK', b'Pakistan'), (b'PL', b'Poland'), (b'PM', b'Saint Pierre and Miquelon'), (b'PN', b'Pitcairn'), (b'PR', b'Puerto Rico'), (b'PS', b'Palestinian Territory'), (b'PT', b'Portugal'), (b'PW', b'Palau'), (b'PY', b'Paraguay'), (b'QA', b'Qatar'), (b'RE', b'Reunion'), (b'RO', b'Romania'), (b'RS', b'Serbia'), (b'RU', b'Russian Federation'), (b'RW', b'Rwanda'), (b'SA', b'Saudi Arabia'), (b'SB', b'Solomon Islands'), (b'SC', b'Seychelles'), (b'SD', b'Sudan'), (b'SE', b'Sweden'), (b'SG', b'Singapore'), (b'SH', b'Saint Helena'), (b'SI', b'Slovenia'), (b'SJ', b'Svalbard and Jan Mayen'), (b'SK', b'Slovakia'), (b'SL', b'Sierra Leone'), (b'SM', b'San Marino'), (b'SN', b'Senegal'), (b'SO', b'Somalia'), (b'SR', b'Suriname'), (b'ST', b'Sao Tome and Principe'), (b'SV', b'El Salvador'), (b'SY', b'Syrian Arab Republic'), (b'SZ', b'Swaziland'), (b'TC', b'Turks and Caicos Islands'), (b'TD', b'Chad'), (b'TF', b'French Southern Territories'), (b'TG', b'Togo'), (b'TH', b'Thailand'), (b'TJ', b'Tajikistan'), (b'TK', b'Tokelau'), (b'TL', b'Timor-Leste'), (b'TM', b'Turkmenistan'), (b'TN', b'Tunisia'), (b'TO', b'Tonga'), (b'TR', b'Turkey'), (b'TT', b'Trinidad and Tobago'), (b'TV', b'Tuvalu'), (b'TW', b'Taiwan'), (b'TZ', b'Tanzania'), (b'UA', b'Ukraine'), (b'UG', b'Uganda'), (b'UM', b'United States Minor Outlying Islands'), (b'UY', b'Uruguay'), (b'UZ', b'Uzbekistan'), (b'VA', b'Vatican City'), (b'VC', b'Saint Vincent and the Grenadines'), (b'VE', b'Venezuela'), (b'VG', b'Virgin Islands (British)'), (b'VI', b'Virgin Islands (US)'), (b'VN', b'Viet Nam'), (b'VU', b'Vanuatu'), (b'WF', b'Wallis and Futuna'), (b'WS', b'Samoa'), (b'YE', b'Yemen'), (b'YT', b'Mayotte'), (b'ZA', b'South Africa'), (b'ZM', b'Zambia'), (b'ZW', b'Zimbabwe')])),
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
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, editable=False, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')])),
                ('action_user', audit_log.models.fields.LastUserField(related_name='_person_audit_log_entry', editable=False, to='karaage.PersonAuditLogEntry', null=True)),
                ('approved_by', models.ForeignKey(related_name='_auditlog_user_approver', blank=True, to='karaage.Person', null=True)),
                ('career_level', models.ForeignKey(related_name='_auditlog_person_set', to='karaage.CareerLevel', null=True)),
                ('deleted_by', models.ForeignKey(related_name='_auditlog_user_deletor', blank=True, to='karaage.Person', null=True)),
                ('institute', models.ForeignKey(related_name='_auditlog_person_set', to='karaage.Institute')),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
        ),
        migrations.AlterField(
            model_name='accountauditlogentry',
            name='default_project',
            field=models.ForeignKey(related_name='_auditlog_account_set', blank=True, to='karaage.Project', null=True),
        ),
        migrations.AlterField(
            model_name='accountauditlogentry',
            name='machine_category',
            field=models.ForeignKey(related_name='_auditlog_account_set', to='karaage.MachineCategory'),
        ),
        migrations.AlterField(
            model_name='accountauditlogentry',
            name='person',
            field=models.ForeignKey(related_name='_auditlog_account_set', to='karaage.Person'),
        ),
        migrations.AlterField(
            model_name='allocationauditlogentry',
            name='allocation_pool',
            field=models.ForeignKey(related_name='_auditlog_allocation_set', to='karaage.AllocationPool'),
        ),
        migrations.AlterField(
            model_name='allocationauditlogentry',
            name='grant',
            field=models.ForeignKey(related_name='_auditlog_allocation_set', to='karaage.Grant'),
        ),
        migrations.AlterField(
            model_name='allocationpoolauditlogentry',
            name='period',
            field=models.ForeignKey(related_name='_auditlog_allocationpool_set', to='karaage.AllocationPeriod'),
        ),
        migrations.AlterField(
            model_name='allocationpoolauditlogentry',
            name='project',
            field=models.ForeignKey(related_name='_auditlog_allocationpool_set', to='karaage.Project'),
        ),
        migrations.AlterField(
            model_name='allocationpoolauditlogentry',
            name='resource_pool',
            field=models.ForeignKey(related_name='_auditlog_allocationpool_set', to='karaage.ResourcePool'),
        ),
        migrations.AlterField(
            model_name='grantauditlogentry',
            name='project',
            field=models.ForeignKey(related_name='_auditlog_grant_set', to='karaage.Project'),
        ),
        migrations.AlterField(
            model_name='grantauditlogentry',
            name='scheme',
            field=models.ForeignKey(related_name='_auditlog_grant_set', to='karaage.Scheme'),
        ),
        migrations.AlterField(
            model_name='instituteauditlogentry',
            name='group',
            field=models.ForeignKey(related_name='_auditlog_institute', to='karaage.Group'),
        ),
        migrations.AlterField(
            model_name='institutedelegateauditlogentry',
            name='institute',
            field=models.ForeignKey(related_name='_auditlog_institutedelegate_set', to='karaage.Institute'),
        ),
        migrations.AlterField(
            model_name='institutedelegateauditlogentry',
            name='person',
            field=models.ForeignKey(related_name='_auditlog_institutedelegate_set', to='karaage.Person'),
        ),
        migrations.AlterField(
            model_name='institutequotaauditlogentry',
            name='institute',
            field=models.ForeignKey(related_name='_auditlog_institutequota_set', to='karaage.Institute'),
        ),
        migrations.AlterField(
            model_name='institutequotaauditlogentry',
            name='machine_category',
            field=models.ForeignKey(related_name='_auditlog_institutequota_set', to='karaage.MachineCategory'),
        ),
        migrations.AlterField(
            model_name='projectauditlogentry',
            name='group',
            field=models.ForeignKey(related_name='_auditlog_project', to='karaage.Group'),
        ),
        migrations.AlterField(
            model_name='projectauditlogentry',
            name='institute',
            field=models.ForeignKey(related_name='_auditlog_project_set', to='karaage.Institute'),
        ),
        migrations.AlterField(
            model_name='projectquotaauditlogentry',
            name='machine_category',
            field=models.ForeignKey(related_name='_auditlog_projectquota_set', to='karaage.MachineCategory'),
        ),
        migrations.AlterField(
            model_name='projectquotaauditlogentry',
            name='project',
            field=models.ForeignKey(related_name='_auditlog_projectquota_set', to='karaage.Project'),
        ),
        migrations.AlterField(
            model_name='resourceauditlogentry',
            name='machine',
            field=models.ForeignKey(related_name='_auditlog_resource_set', to='karaage.Machine'),
        ),
        migrations.AlterField(
            model_name='resourceauditlogentry',
            name='resource_pool',
            field=models.ForeignKey(related_name='_auditlog_resource_set', to='karaage.ResourcePool'),
        ),
        migrations.AlterField(
            model_name='resourcepoolauditlogentry',
            name='content_type',
            field=models.ForeignKey(related_name='_auditlog_resourcepool_set', to='contenttypes.ContentType'),
        ),
    ]

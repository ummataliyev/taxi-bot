# Generated by Django 4.2.4 on 2023-08-18 10:38

from django.db import migrations

def populate_regions_and_districts(apps, schema_editor):
    Region = apps.get_model('data', 'Province')
    District = apps.get_model('data', 'District')
    
    # Regions
    regions = [
        'Farg\'ona',
        'Tashkent'
    ]
    
    # Districts of Farg'ona region
    fargona_districts = [
        'Beshariq',
        'Bog\'dod',
        'Farg\'ona shahar',
        'Farg\'ona tumani',
        'Furqat',
        'Kirguli',
        'Kuva',
        'Marg\'ilon shahar',
        'O\'zbekiston',
        'Quva',
        'Rishton',
        'So\'x',
        'Toshloq',
        'Uchko\'prik',
        'Yozuvchi'
    ]
    
    # Districts of Tashkent region
    tashkent_districts = [
        'Bekobod',
        'Bektemir',
        'Bostanlik',
        'Chilonzor',
        'Mirobod',
        'Mirzo-Ulug\'bek',
        'Olmazor',
        'Sergeli',
        'Shayhontohur',
        'Uchtepa',
        'Yakkasaray',
        'Yashnobod',
        'Yunusobod'
    ]

    for region_name in regions:
        region = Region.objects.create(name=region_name)
        
        if region_name == 'Farg\'ona':
            for district_name in fargona_districts:
                District.objects.create(name=district_name, province=region)
        
        elif region_name == 'Tashkent':
            for district_name in tashkent_districts:
                District.objects.create(name=district_name, province=region)



class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_regions_and_districts),
    ]

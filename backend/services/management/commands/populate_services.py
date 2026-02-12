from django.core.management.base import BaseCommand
from backend.services.models import Service


class Command(BaseCommand):
    help = 'Populate the database with basic salon services'

    def handle(self, *args, **kwargs):
        services_data = [
            {
                'name': 'Women\'s Haircut',
                'description': 'Professional haircut and styling for women. Includes consultation, wash, cut, and blow-dry.',
                'price': 45.00,
                'duration': 60
            },
            {
                'name': 'Men\'s Haircut',
                'description': 'Classic men\'s haircut with styling. Includes consultation, wash, cut, and styling.',
                'price': 30.00,
                'duration': 45
            },
            {
                'name': 'Hair Coloring',
                'description': 'Full hair coloring service with premium color products. Includes color consultation and treatment.',
                'price': 85.00,
                'duration': 120
            },
            {
                'name': 'Highlights',
                'description': 'Partial or full highlights to add dimension and brightness to your hair.',
                'price': 95.00,
                'duration': 150
            },
            {
                'name': 'Box Braids',
                'description': 'Traditional box braids styled to perfection. Protective styling that lasts weeks.',
                'price': 150.00,
                'duration': 240
            },
            {
                'name': 'Cornrows',
                'description': 'Professional cornrow braiding in various styles and patterns.',
                'price': 75.00,
                'duration': 120
            },
            {
                'name': 'Knotless Braids',
                'description': 'Trendy knotless braids for a lighter, more natural look without tension.',
                'price': 180.00,
                'duration': 300
            },
            {
                'name': 'Manicure',
                'description': 'Complete manicure service including nail shaping, cuticle care, and polish application.',
                'price': 35.00,
                'duration': 45
            },
            {
                'name': 'Pedicure',
                'description': 'Relaxing pedicure with foot soak, exfoliation, massage, and polish.',
                'price': 45.00,
                'duration': 60
            },
            {
                'name': 'Gel Nails',
                'description': 'Long-lasting gel nail application with UV curing for durable, glossy finish.',
                'price': 55.00,
                'duration': 75
            },
            {
                'name': 'Facial Treatment',
                'description': 'Deep cleansing facial with exfoliation, mask, and moisturizing treatment.',
                'price': 70.00,
                'duration': 60
            },
            {
                'name': 'Eyebrow Shaping',
                'description': 'Professional eyebrow shaping and grooming to enhance your natural features.',
                'price': 20.00,
                'duration': 30
            },
            {
                'name': 'Waxing Service',
                'description': 'Full body waxing services available. Smooth, long-lasting results.',
                'price': 40.00,
                'duration': 45
            },
            {
                'name': 'Hair Treatment',
                'description': 'Deep conditioning treatment to repair and nourish damaged hair.',
                'price': 50.00,
                'duration': 60
            },
            {
                'name': 'Blowout',
                'description': 'Professional blowout styling for smooth, voluminous hair.',
                'price': 40.00,
                'duration': 45
            },
            {
                'name': 'Updo Styling',
                'description': 'Elegant updo styling perfect for special occasions and events.',
                'price': 65.00,
                'duration': 75
            },
            {
                'name': 'Keratin Treatment',
                'description': 'Smoothing keratin treatment to eliminate frizz and add shine.',
                'price': 200.00,
                'duration': 180
            },
            {
                'name': 'Makeup Application',
                'description': 'Professional makeup application for any occasion.',
                'price': 55.00,
                'duration': 60
            },
        ]

        created_count = 0
        updated_count = 0

        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'duration': service_data['duration'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {service.name}'))
            else:
                # Update existing service
                service.description = service_data['description']
                service.price = service_data['price']
                service.duration = service_data['duration']
                service.is_active = True
                service.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {service.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully processed {created_count + updated_count} services'))
        self.stdout.write(self.style.SUCCESS(f'  - Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  - Updated: {updated_count}'))

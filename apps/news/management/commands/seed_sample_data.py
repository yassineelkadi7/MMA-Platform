"""
Management command to seed sample MMA news articles and events for development.

Usage:
    python manage.py seed_sample_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Seed the database with sample MMA news articles and events for development."

    def handle(self, *args, **options):
        self._seed_articles()
        self._seed_events()
        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully."))

    def _seed_articles(self):
        from apps.news.models import Article

        articles = [
            {
                "external_id": "sample-ufc-300-preview",
                "title": "UFC 300: The Most Anticipated Card in UFC History",
                "summary": "UFC 300 promises to be a historic event with multiple championship bouts and legendary matchups. Alex Pereira defends his light heavyweight title against Jamahal Hill in the main event.",
                "source_name": "MMA Fighting",
                "source_url": "https://www.mmafighting.com/ufc-300-preview",
                "image_url": "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=600&q=80",
                "category": "preview",
                "published_at": timezone.now() - timedelta(days=1),
            },
            {
                "external_id": "sample-jones-miocic",
                "title": "Jon Jones vs Stipe Miocic: Heavyweight Title Fight Set for UFC 309",
                "summary": "Jon Jones will defend his heavyweight championship against former champion Stipe Miocic at UFC 309. Jones has been dominant since moving up to heavyweight, while Miocic looks to reclaim his title.",
                "source_name": "ESPN MMA",
                "source_url": "https://www.espn.com/mma/jones-miocic",
                "image_url": "https://images.unsplash.com/photo-1517438476312-10d79c077509?w=600&q=80",
                "category": "fighter",
                "published_at": timezone.now() - timedelta(days=2),
            },
            {
                "external_id": "sample-islam-makhachev",
                "title": "Islam Makhachev Dominates Dustin Poirier at UFC 302",
                "summary": "Islam Makhachev successfully defended his lightweight championship with a dominant performance against Dustin Poirier. The Dagestani fighter showcased his elite grappling and improved striking.",
                "source_name": "UFC.com",
                "source_url": "https://www.ufc.com/news/makhachev-poirier-results",
                "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80",
                "category": "results",
                "published_at": timezone.now() - timedelta(days=3),
            },
            {
                "external_id": "sample-conor-return",
                "title": "Conor McGregor Return Fight Officially Announced",
                "summary": "Conor McGregor is set to return to the octagon after a lengthy absence. The former two-division champion will face Michael Chandler in a highly anticipated welterweight bout.",
                "source_name": "Bloody Elbow",
                "source_url": "https://www.bloodyelbow.com/mcgregor-return",
                "image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&q=80",
                "category": "fighter",
                "published_at": timezone.now() - timedelta(days=4),
            },
            {
                "external_id": "sample-ufc-rankings",
                "title": "UFC Rankings Update: Major Shifts After Recent Events",
                "summary": "The latest UFC rankings show significant movement across multiple divisions following recent fight cards. Several fighters have broken into the top 10 after impressive performances.",
                "source_name": "MMA Junkie",
                "source_url": "https://mmajunkie.usatoday.com/rankings-update",
                "image_url": "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=600&q=80",
                "category": "general",
                "published_at": timezone.now() - timedelta(days=5),
            },
            {
                "external_id": "sample-boxing-fury-usyk",
                "title": "Fury vs Usyk 2: Rematch Confirmed for December",
                "summary": "Tyson Fury and Oleksandr Usyk will meet in a rematch for the undisputed heavyweight championship. The first fight ended in a controversial split decision victory for Usyk.",
                "source_name": "Boxing Scene",
                "source_url": "https://www.boxingscene.com/fury-usyk-rematch",
                "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",
                "category": "general",
                "published_at": timezone.now() - timedelta(days=6),
            },
            {
                "external_id": "sample-pereira-dominick",
                "title": "Alex Pereira: 'I Will Knock Out Everyone in My Path'",
                "summary": "Light heavyweight champion Alex Pereira spoke about his future plans and upcoming title defense. The Brazilian knockout artist has been one of the most exciting fighters in the UFC.",
                "source_name": "MMA Fighting",
                "source_url": "https://www.mmafighting.com/pereira-interview",
                "image_url": "https://images.unsplash.com/photo-1552072092-7f9b8d63efcb?w=600&q=80",
                "category": "fighter",
                "published_at": timezone.now() - timedelta(days=7),
            },
            {
                "external_id": "sample-ufc-fight-night",
                "title": "UFC Fight Night Results: Holloway Stops Gaethje in Stunning Fashion",
                "summary": "Max Holloway delivered one of the most memorable moments in UFC history, stopping Justin Gaethje with a last-second knockout at the final bell of their BMF title fight.",
                "source_name": "UFC.com",
                "source_url": "https://www.ufc.com/news/holloway-gaethje-results",
                "image_url": "https://images.unsplash.com/photo-1593079831268-3381b0db4a77?w=600&q=80",
                "category": "results",
                "published_at": timezone.now() - timedelta(days=8),
            },
        ]

        created = 0
        updated = 0
        for data in articles:
            obj, was_created = Article.objects.get_or_create(
                external_id=data["external_id"],
                defaults=data,
            )
            if was_created:
                created += 1
            elif not obj.image_url and data.get("image_url"):
                # Update image_url on existing articles that don't have one yet
                obj.image_url = data["image_url"]
                obj.save(update_fields=["image_url"])
                updated += 1

        self.stdout.write(f"  Articles: {created} created, {updated} image(s) updated ({len(articles) - created - updated} unchanged)")

    def _seed_events(self):
        from apps.events.models import WeightClass, Fighter, Event, Fight

        # Create weight classes
        weight_classes = {
            "Heavyweight": WeightClass.objects.get_or_create(name="Heavyweight", defaults={"limit_kg": 120.2})[0],
            "Light Heavyweight": WeightClass.objects.get_or_create(name="Light Heavyweight", defaults={"limit_kg": 93.0})[0],
            "Middleweight": WeightClass.objects.get_or_create(name="Middleweight", defaults={"limit_kg": 83.9})[0],
            "Welterweight": WeightClass.objects.get_or_create(name="Welterweight", defaults={"limit_kg": 77.1})[0],
            "Lightweight": WeightClass.objects.get_or_create(name="Lightweight", defaults={"limit_kg": 70.3})[0],
            "Featherweight": WeightClass.objects.get_or_create(name="Featherweight", defaults={"limit_kg": 65.8})[0],
        }

        # Create fighters
        fighters_data = [
            {"external_id": "f-jones", "full_name": "Jon Jones", "nationality": "American", "weight_class": "Heavyweight", "fighting_style": "Wrestling/BJJ", "wins": 27, "losses": 1, "draws": 0},
            {"external_id": "f-miocic", "full_name": "Stipe Miocic", "nationality": "American", "weight_class": "Heavyweight", "fighting_style": "Boxing/Wrestling", "wins": 20, "losses": 4, "draws": 0},
            {"external_id": "f-pereira", "full_name": "Alex Pereira", "nationality": "Brazilian", "weight_class": "Light Heavyweight", "fighting_style": "Kickboxing", "wins": 10, "losses": 2, "draws": 0},
            {"external_id": "f-hill", "full_name": "Jamahal Hill", "nationality": "American", "weight_class": "Light Heavyweight", "fighting_style": "Boxing", "wins": 12, "losses": 2, "draws": 0},
            {"external_id": "f-makhachev", "full_name": "Islam Makhachev", "nationality": "Russian", "weight_class": "Lightweight", "fighting_style": "Sambo/Wrestling", "wins": 25, "losses": 1, "draws": 0},
            {"external_id": "f-poirier", "full_name": "Dustin Poirier", "nationality": "American", "weight_class": "Lightweight", "fighting_style": "Boxing/BJJ", "wins": 30, "losses": 9, "draws": 0},
            {"external_id": "f-holloway", "full_name": "Max Holloway", "nationality": "American", "weight_class": "Featherweight", "fighting_style": "Boxing", "wins": 25, "losses": 7, "draws": 0},
            {"external_id": "f-gaethje", "full_name": "Justin Gaethje", "nationality": "American", "weight_class": "Lightweight", "fighting_style": "Wrestling/Boxing", "wins": 25, "losses": 5, "draws": 0},
        ]

        fighters = {}
        for data in fighters_data:
            wc = weight_classes.get(data.pop("weight_class"))
            fighter, _ = Fighter.objects.get_or_create(
                external_id=data["external_id"],
                defaults={**data, "weight_class": wc},
            )
            fighters[fighter.external_id] = fighter

        # Create upcoming events
        events_data = [
            {
                "external_id": "evt-ufc-309",
                "name": "UFC 309: Jones vs Miocic",
                "date": timezone.now() + timedelta(days=15),
                "location": "New York, NY",
                "venue": "Madison Square Garden",
                "broadcast_info": "PPV on ESPN+",
                "status": "upcoming",
            },
            {
                "external_id": "evt-ufc-310",
                "name": "UFC 310: Pereira vs Hill 2",
                "date": timezone.now() + timedelta(days=45),
                "location": "Las Vegas, NV",
                "venue": "T-Mobile Arena",
                "broadcast_info": "PPV on ESPN+",
                "status": "upcoming",
            },
            {
                "external_id": "evt-ufc-fn-dec",
                "name": "UFC Fight Night: Makhachev vs Poirier 2",
                "date": timezone.now() + timedelta(days=30),
                "location": "Abu Dhabi, UAE",
                "venue": "Etihad Arena",
                "broadcast_info": "ESPN+",
                "status": "upcoming",
            },
            {
                "external_id": "evt-ufc-308-past",
                "name": "UFC 308: Holloway vs Gaethje",
                "date": timezone.now() - timedelta(days=10),
                "location": "Abu Dhabi, UAE",
                "venue": "Etihad Arena",
                "broadcast_info": "PPV on ESPN+",
                "status": "completed",
            },
        ]

        events = {}
        for data in events_data:
            event, _ = Event.objects.get_or_create(
                external_id=data["external_id"],
                defaults=data,
            )
            events[event.external_id] = event

        # Create fights for UFC 309
        ufc309 = events.get("evt-ufc-309")
        if ufc309:
            Fight.objects.get_or_create(
                event=ufc309,
                fighter_a=fighters["f-jones"],
                fighter_b=fighters["f-miocic"],
                defaults={"is_main_event": True, "bout_order": 1},
            )

        # Create fights for UFC 310
        ufc310 = events.get("evt-ufc-310")
        if ufc310:
            Fight.objects.get_or_create(
                event=ufc310,
                fighter_a=fighters["f-pereira"],
                fighter_b=fighters["f-hill"],
                defaults={"is_main_event": True, "bout_order": 1},
            )

        # Create fights for past event with results
        past_event = events.get("evt-ufc-308-past")
        if past_event:
            Fight.objects.get_or_create(
                event=past_event,
                fighter_a=fighters["f-holloway"],
                fighter_b=fighters["f-gaethje"],
                defaults={
                    "is_main_event": True,
                    "bout_order": 1,
                    "winner": fighters["f-holloway"],
                    "method": "ko",
                },
            )

        self.stdout.write(f"  Events: {len(events_data)} processed, fighters: {len(fighters_data)} processed")

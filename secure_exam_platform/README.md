# Secure Exam Platform (Django)

Plateforme d'examen web anti-triche pour universités.

## Stack
- Django + DRF + JWT
- Django Channels + Redis
- PostgreSQL
- Celery
- JavaScript (MediaDevices, Fullscreen, WebSocket)

## Démarrage rapide
```bash
docker compose up --build
```

## Fonctionnalités clés
- Sessions d'examen avec minuteur côté serveur.
- Surveillance anti-triche en temps réel (tab switch, fullscreen, copy/paste, webcam).
- Snapshots webcam/capture écran envoyés au backend.
- Dashboard admin live via WebSocket.
- Auto-soumission en cas d'expiration ou fermeture forcée.
- Journalisation des événements sécurité (`SecurityEvent`).

## Endpoints API
- `POST /api/sessions/start/`
- `POST /api/sessions/{id}/submit/`
- `POST /api/sessions/{id}/close/`
- `GET /api/sessions/{id}/questions/`

## Exécution tests
```bash
python manage.py test tests
```

## Seed
```bash
python manage.py shell -c "from scripts.seed_exams import run; run()"
```

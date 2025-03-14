import os
import shutil
import datetime
from pathlib import Path
from django.conf import settings
from django.core.management import call_command

def create_backup():
    """Create a backup of the database and media files."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(settings.BACKUP_ROOT) / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup database
    db_backup_path = backup_dir / 'db.json'
    with open(db_backup_path, 'w') as f:
        call_command('dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes', 
                    '--indent', '2', stdout=f)
    
    # Backup media files
    if not settings.USE_S3:
        media_backup_path = backup_dir / 'media'
        shutil.copytree(settings.MEDIA_ROOT, media_backup_path)
    
    # Clean old backups
    cleanup_old_backups()
    
    return backup_dir

def restore_backup(backup_dir):
    """Restore database and media files from a backup."""
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        raise ValueError(f'Backup directory {backup_dir} does not exist')
    
    # Restore database
    db_backup_path = backup_path / 'db.json'
    if db_backup_path.exists():
        call_command('loaddata', str(db_backup_path))
    
    # Restore media files
    if not settings.USE_S3:
        media_backup_path = backup_path / 'media'
        if media_backup_path.exists():
            if settings.MEDIA_ROOT.exists():
                shutil.rmtree(settings.MEDIA_ROOT)
            shutil.copytree(media_backup_path, settings.MEDIA_ROOT)

def cleanup_old_backups():
    """Remove old backups keeping only the specified number of recent backups."""
    backup_root = Path(settings.BACKUP_ROOT)
    if not backup_root.exists():
        return
    
    # Get list of backup directories sorted by creation time
    backups = [(d, d.stat().st_ctime) for d in backup_root.iterdir() if d.is_dir()]
    backups.sort(key=lambda x: x[1], reverse=True)
    
    # Remove old backups
    for backup_dir, _ in backups[settings.BACKUP_COUNT:]:
        shutil.rmtree(backup_dir)

def list_backups():
    """List all available backups."""
    backup_root = Path(settings.BACKUP_ROOT)
    if not backup_root.exists():
        return []
    
    backups = [(d, d.stat().st_ctime) for d in backup_root.iterdir() if d.is_dir()]
    backups.sort(key=lambda x: x[1], reverse=True)
    
    return [{
        'name': backup_dir.name,
        'created_at': datetime.datetime.fromtimestamp(created_at),
        'size': sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
    } for backup_dir, created_at in backups]
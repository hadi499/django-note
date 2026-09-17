from django.db import models

class Folder(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        import re
        import os
        from django.conf import settings
        
        # Cari semua URL gambar di dalam konten
        img_urls = re.findall(r'<img[^>]+src="([^">]+)"', self.content)
        for url in img_urls:
            # Pastikan URL mengarah ke media lokal kita
            if url.startswith(settings.MEDIA_URL):
                filename = url[len(settings.MEDIA_URL):]
                filename = os.path.basename(filename)
                file_path = os.path.join(settings.MEDIA_ROOT, filename)
                # Hapus dari disk lokal
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
        # Lanjutkan penghapusan Note dari database
        super().delete(*args, **kwargs)

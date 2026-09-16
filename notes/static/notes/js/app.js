let quill = null;

if (typeof QuillBlotFormatter !== 'undefined') {
    Quill.register('modules/blotFormatter', QuillBlotFormatter.default);
    
    // Custom Action to add a visual Trash/Delete button
    window.TrashAction = class extends QuillBlotFormatter.Action {
        onCreate() {
            this.button = document.createElement('div');
            this.button.innerHTML = '🗑️';
            Object.assign(this.button.style, {
                position: 'absolute',
                top: '-25px',
                right: '0',
                cursor: 'pointer',
                background: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px',
                padding: '2px 6px',
                fontSize: '14px',
                zIndex: '10',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            });
            
            this.button.addEventListener('mousedown', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.formatter.currentSpec) {
                    const target = this.formatter.currentSpec.getTargetElement();
                    if (target) {
                        const imgUrl = target.getAttribute('src');
                        
                        // Extract CSRF token
                        let csrfToken = '';
                        const hxHeaders = document.body.getAttribute('hx-headers');
                        if (hxHeaders) {
                            try {
                                const headers = JSON.parse(hxHeaders);
                                csrfToken = headers['X-CSRFToken'] || '';
                            } catch(err) {}
                        }

                        // Send delete request to backend instantly
                        if (imgUrl && imgUrl.startsWith('/media/')) {
                            try {
                                await fetch('/delete-image/', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': csrfToken
                                    },
                                    body: JSON.stringify({ url: imgUrl })
                                });
                            } catch (err) {
                                console.error('Failed to delete image from backend', err);
                            }
                        }

                        // Remove from editor
                        const blot = Quill.find(target);
                        if (blot) {
                            blot.deleteAt(0, blot.length());
                        } else {
                            target.remove();
                        }
                    }
                    this.formatter.hide();
                }
            });
            
            this.formatter.overlay.appendChild(this.button);
        }

        onDestroy() {
            if (this.button) {
                this.button.remove();
                this.button = null;
            }
        }
    };

    window.CustomImageSpec = class extends QuillBlotFormatter.ImageSpec {
        getActions() {
            return [
                QuillBlotFormatter.AlignAction,
                QuillBlotFormatter.ResizeAction,
                QuillBlotFormatter.DeleteAction, // For keyboard backspace
                window.TrashAction // For visual button
            ];
        }
    };
}

window.cleanupUnsavedImages = function() {
    if (document.getElementById('editor')) {
        const images = document.querySelectorAll('.ql-editor img');
        let csrfToken = '';
        try {
            const hxHeaders = document.body.getAttribute('hx-headers');
            if (hxHeaders) {
                const headers = JSON.parse(hxHeaders);
                csrfToken = headers['X-CSRFToken'] || '';
            }
        } catch(e) {}
        
        images.forEach(img => {
            const imgUrl = img.getAttribute('src');
            if (imgUrl && imgUrl.startsWith('/media/')) {
                fetch('/delete-image/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ url: imgUrl })
                }).catch(err => console.error(err));
            }
        });
    }
};

function initQuill() {
    if (document.getElementById('editor')) {
        quill = new Quill('#editor', {
            theme: 'snow',
            bounds: '#editor',
            placeholder: 'Write your note here...',
            modules: {
                formula: true,
                blotFormatter: {
                    specs: [
                        window.CustomImageSpec
                    ]
                },
                toolbar: {
                    container: [
                        [{ 'header': [1, 2, 3, false] }],
                        ['bold', 'italic', 'underline', 'strike'],
                        ['blockquote', 'code-block', 'formula'],
                        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                        [{ 'color': [] }, { 'background': [] }],
                        ['image', 'clean']
                    ],
                    handlers: {
                        image: imageHandler
                    }
                }
            }
        });
        
        function imageHandler() {
            const input = document.createElement('input');
            input.setAttribute('type', 'file');
            input.setAttribute('accept', 'image/*');
            input.click();

            input.onchange = async () => {
                const file = input.files[0];
                const formData = new FormData();
                formData.append('image', file);

                let csrfToken = '';
                const hxHeaders = document.body.getAttribute('hx-headers');
                if (hxHeaders) {
                    try {
                        const headers = JSON.parse(hxHeaders);
                        csrfToken = headers['X-CSRFToken'] || '';
                    } catch(e) {}
                }

                try {
                    const response = await fetch('/upload-image/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken
                        },
                        body: formData
                    });

                    if (response.ok) {
                        const data = await response.json();
                        const range = quill.getSelection(true);
                        quill.insertEmbed(range.index, 'image', data.url);
                    } else {
                        console.error('Upload failed');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            };
        }
        
        // Update hidden input on change
        quill.on('text-change', function() {
            const contentInput = document.getElementById('content');
            if (contentInput) {
                contentInput.value = quill.root.innerHTML;
            }
        });
        
        // Initialize hidden input with current value
        const contentInput = document.getElementById('content');
        if (contentInput) {
            contentInput.value = quill.root.innerHTML;
        }
    }
}

// Initial check when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Basic setup, but HTMX will handle navigation mostly.
});

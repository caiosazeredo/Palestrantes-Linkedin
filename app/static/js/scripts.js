// Scripts para a aplicação

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar Select2 para melhorar os selects múltiplos
    if ($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap-5',
            width: '100%',
            placeholder: 'Selecione...',
            allowClear: true
        });
    }
    
    // Confirmação de exclusão
    const confirmDeleteForms = document.querySelectorAll('.confirm-delete');
    
    confirmDeleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const itemName = this.getAttribute('data-item-name') || 'este item';
            
            if (confirm(`Tem certeza que deseja excluir ${itemName}? Esta ação não pode ser desfeita.`)) {
                this.submit();
            }
        });
    });
    
    // Contador de caracteres para textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counterElement = document.createElement('div');
        counterElement.className = 'text-muted text-end small mt-1';
        counterElement.innerHTML = `<span class="current-length">0</span>/${maxLength} caracteres`;
        
        textarea.parentNode.appendChild(counterElement);
        
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            const counter = this.parentNode.querySelector('.current-length');
            counter.textContent = currentLength;
            
            // Estilizar o contador quando estiver chegando ao limite
            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
        
        // Atualizar contador na inicialização
        const event = new Event('input');
        textarea.dispatchEvent(event);
    });
    
    // Validação de formulários no lado do cliente
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Mostrar preview da imagem selecionada
    const imageInputs = document.querySelectorAll('.image-input');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewId = this.getAttribute('data-preview');
            const previewElement = document.getElementById(previewId);
            
            if (previewElement && this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewElement.src = e.target.result;
                    previewElement.style.display = 'block';
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Máscaras para entrada de dados
    const phoneMasks = document.querySelectorAll('.phone-mask');
    
    phoneMasks.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            
            if (value.length <= 10) {
                // Formato (XX) XXXX-XXXX
                if (value.length > 2) {
                    value = '(' + value.substring(0, 2) + ') ' + value.substring(2);
                }
                if (value.length > 9) {
                    value = value.substring(0, 9) + '-' + value.substring(9);
                }
            } else {
                // Formato (XX) XXXXX-XXXX
                value = '(' + value.substring(0, 2) + ') ' + value.substring(2, 7) + '-' + value.substring(7, 11);
            }
            
            this.value = value;
        });
    });
});

// Funções para manipulação de dados do LinkedIn
function importarPerfilLinkedIn(perfil) {
    // Preencher o formulário com os dados do perfil
    document.getElementById('importar-nome').value = perfil.nome || '';
    document.getElementById('importar-cargo').value = perfil.cargo_atual || '';
    document.getElementById('importar-empresa').value = perfil.empresa_atual || '';
    document.getElementById('importar-perfil-url').value = perfil.perfil_url || '';
    document.getElementById('importar-bio').value = perfil.bio || '';
    document.getElementById('importar-foto-url').value = perfil.foto_url || '';
    document.getElementById('importar-seguidores').value = perfil.seguidores || '0';
    
    // Habilidades como string separada por vírgulas
    document.getElementById('importar-habilidades').value = 
        Array.isArray(perfil.habilidades) ? perfil.habilidades.join(', ') : '';
    
    // Mostrar o modal de importação
    const modal = new bootstrap.Modal(document.getElementById('modal-importar-linkedin'));
    modal.show();
}
/**
 * Reusable Dynamic Modal Manager
 */
const Modal = {
  activeModal: null,

  open(modalId) {
    const el = document.getElementById(modalId);
    if (!el) return;
    el.classList.add('active');
    this.activeModal = el;
    document.body.style.overflow = 'hidden';

    // Auto focus first input
    const input = el.querySelector('input:not([type=hidden]), textarea, select');
    if (input) setTimeout(() => input.focus(), 100);
  },

  close(modalId = null) {
    const el = modalId ? document.getElementById(modalId) : this.activeModal;
    if (!el) return;
    el.classList.remove('active');
    this.activeModal = null;
    document.body.style.overflow = '';
  },

  confirm({ title, message, confirmText = 'Confirm', confirmClass = 'btn-primary', onConfirm }) {
    let confirmModal = document.getElementById('global-confirm-modal');
    if (!confirmModal) {
      confirmModal = document.createElement('div');
      confirmModal.id = 'global-confirm-modal';
      confirmModal.className = 'modal-backdrop';
      confirmModal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-header">
            <h3 class="modal-title" id="confirm-modal-title">Confirmation</h3>
            <button class="modal-close-btn" onclick="Modal.close('global-confirm-modal')">&times;</button>
          </div>
          <div class="modal-body">
            <p id="confirm-modal-message" style="color:var(--text-main); font-size:1rem;"></p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="Modal.close('global-confirm-modal')">Cancel</button>
            <button id="confirm-modal-action-btn" class="btn btn-primary">Confirm</button>
          </div>
        </div>
      `;
      document.body.appendChild(confirmModal);
    }

    document.getElementById('confirm-modal-title').textContent = title;
    document.getElementById('confirm-modal-message').textContent = message;
    
    const actionBtn = document.getElementById('confirm-modal-action-btn');
    actionBtn.className = `btn ${confirmClass}`;
    actionBtn.textContent = confirmText;
    
    // Replace listener cleanly
    const newBtn = actionBtn.cloneNode(true);
    actionBtn.parentNode.replaceChild(newBtn, actionBtn);
    newBtn.addEventListener('click', () => {
      Modal.close('global-confirm-modal');
      if (typeof onConfirm === 'function') onConfirm();
    });

    this.open('global-confirm-modal');
  }
};

// Global Esc key listener for active modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && Modal.activeModal) {
    Modal.close();
  }
});

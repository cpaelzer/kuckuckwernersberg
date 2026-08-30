// SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
// SPDX-License-Identifier: GPL-3.0-or-later

(function () {
  const WRONG_MSG = 'Das war leider der falsche Vogel, hast Du ihn wirklich gefunden?';
  const CORRECT_MSG = 'Ja genau, doch leider ist das noch nicht Werner, lass uns weiter suchen.';

  const modal = document.getElementById('bird-modal');
  const modalMsg = document.getElementById('modal-message');
  const modalClose = document.getElementById('modal-close');
  const modalContent = modal ? modal.querySelector('.modal-content') : null;

  if (!modal) return;

  modalClose.addEventListener('click', function () {
    modal.classList.remove('visible');
    if (modalContent) {
      modalContent.classList.remove('success', 'failure');
    }
  });

  modal.addEventListener('click', function (e) {
    if (e.target === modal) {
      modal.classList.remove('visible');
      if (modalContent) {
        modalContent.classList.remove('success', 'failure');
      }
    }
  });

  var options = document.querySelectorAll('.bird-option');
  options.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var correctPrefix = this.getAttribute('data-correct-prefix');
      var isCorrect = this.classList.contains('correct');

      if (isCorrect) {
        modalMsg.textContent = CORRECT_MSG;
        modalContent.classList.remove('failure');
        modalContent.classList.add('success');
      } else {
        modalMsg.textContent = WRONG_MSG;
        modalContent.classList.remove('success');
        modalContent.classList.add('failure');
      }

      modal.classList.add('visible');
    });
  });

  // Mark correct option with a hint
  var correctEl = document.querySelector('.bird-option.correct');
  if (correctEl) {
    // Remove the incorrect hint for correct so it's indistinguishable until clicked
  }
})();
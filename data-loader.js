// ============================================
// DATA LOADER — Chargement dynamique par recrutement
// ============================================

// Récupère ID recrutement depuis URL ou localStorage
function getActiveRecruitmentId() {
  const params = new URLSearchParams(window.location.search);
  let id = params.get('r') || params.get('recruitment');

  if (!id) {
    id = sessionStorage.getItem('activeRecruitment');
  }

  return id || null;
}

// Charge manifest (liste des recrutements disponibles)
async function loadManifest() {
  try {
    const res = await fetch('/recrutements/manifest.json');
    if (!res.ok) throw new Error(`Manifest fetch failed: ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn('Manifest not found, using empty list');
    return [];
  }
}

// Charge config + data pour un recrutement
async function loadRecruitmentData(recruitmentId) {
  try {
    const [configRes, dataRes] = await Promise.all([
      fetch(`/recrutements/${recruitmentId}/config.json`),
      fetch(`/recrutements/${recruitmentId}/data.json`)
    ]);

    if (!configRes.ok || !dataRes.ok) {
      throw new Error(`Recruitment ${recruitmentId} not found`);
    }

    const config = await configRes.json();
    const data = await dataRes.json();

    // Injecte les données globales
    window.RECRUITMENT_ID = recruitmentId;
    window.RECRUITMENT_CONFIG = config;
    window.CRITERIA = config.criteria || [];
    window.CANDIDATES = data.candidates || {};
    window.DECISION_OPTIONS = config.decisionOptions || ['À convoquer', 'Convoqué', 'Retenu', 'Non retenu'];

    // Calcule MAX_SCORE (support scoreOptions custom ou fallback 1-5)
    window.MAX_SCORE = CRITERIA.reduce((sum, c) => {
      if (c.scoreOptions) {
        return sum + Math.max(...c.scoreOptions) * (c.coeff || 1);
      }
      return sum + (c.coeff || 1) * 5;
    }, 0);

    // Définit catégories par défaut si non fournies
    if (!window.QUESTION_CATEGORIES) {
      window.QUESTION_CATEGORIES = {
        motivation: { label: 'Motivation / Reconversion', icon: '🎯' },
        experience: { label: 'Expérience commerciale', icon: '💼' },
        technique: { label: 'Connaissance technique BTP', icon: '🔧' },
        secteur: { label: 'Gestion de secteur', icon: '🗺️' },
        softskills: { label: 'Soft skills / Fit culture', icon: '🤝' },
        specifiques: { label: 'Questions spécifiques au profil', icon: '🔍' }
      };
    }

    console.log(`✓ Recrutement chargé: ${recruitmentId}`);
    console.log(`  - ${Object.keys(CANDIDATES).length} candidats`);
    console.log(`  - ${CRITERIA.length} critères`);

    return true;
  } catch (e) {
    console.error('Erreur chargement recrutement:', e);
    return false;
  }
}

// Affiche modale de sélection recrutement
async function showRecruitmentModal() {
  const manifest = await loadManifest();

  if (manifest.length === 0) {
    console.warn('Aucun recrutement disponible');
    return null;
  }

  // Si un seul recrutement, sélectionne automatiquement
  if (manifest.length === 1) {
    sessionStorage.setItem('activeRecruitment', manifest[0].id);
    return manifest[0].id;
  }

  // Plusieurs recrutements : affiche modale
  return new Promise((resolve) => {
    const modalHtml = `
      <div id="recruitmentModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Sélectionnez un recrutement</h2>
          <div class="space-y-2 mb-6" id="recruitmentList"></div>
          <div id="customRecruitmentInput" class="hidden flex gap-2">
            <input id="customRecIdInput" type="text" placeholder="ID recrutement..." class="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-yellow-400 focus:outline-none">
            <button onclick="loadCustomRecruitment()" class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white rounded text-sm font-medium">OK</button>
          </div>
          <button onclick="toggleCustomInput()" class="w-full text-xs text-gray-500 hover:text-gray-700 py-2 mt-4 border-t">Autre...</button>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    const list = document.getElementById('recruitmentList');
    manifest.forEach(rec => {
      const btn = document.createElement('button');
      btn.className = 'w-full text-left px-4 py-3 rounded border border-gray-200 hover:bg-yellow-50 hover:border-yellow-400 transition font-medium text-gray-900';
      btn.innerHTML = `
        <div>${rec.title}</div>
        <div class="text-xs text-gray-500">${rec.subtitle || ''}</div>
      `;
      btn.onclick = () => {
        sessionStorage.setItem('activeRecruitment', rec.id);
        document.getElementById('recruitmentModal').remove();
        resolve(rec.id);
      };
      list.appendChild(btn);
    });

    window.toggleCustomInput = () => {
      const input = document.getElementById('customRecruitmentInput');
      input.classList.toggle('hidden');
      if (!input.classList.contains('hidden')) {
        document.getElementById('customRecIdInput').focus();
      }
    };

    window.loadCustomRecruitment = () => {
      const id = document.getElementById('customRecIdInput').value.trim();
      if (id) {
        sessionStorage.setItem('activeRecruitment', id);
        document.getElementById('recruitmentModal').remove();
        resolve(id);
      }
    };
  });
}

// Initialisation
async function initRecruitmentSelector() {
  let recruitmentId = getActiveRecruitmentId();
  console.log('[DEBUG] getActiveRecruitmentId:', recruitmentId);

  if (!recruitmentId) {
    recruitmentId = await showRecruitmentModal();
    console.log('[DEBUG] showRecruitmentModal selected:', recruitmentId);
  }

  if (!recruitmentId) {
    console.error('Pas de recrutement sélectionné');
    return false;
  }

  const result = await loadRecruitmentData(recruitmentId);
  console.log('[DEBUG] loadRecruitmentData result:', result, 'CANDIDATES length:', Object.keys(window.CANDIDATES || {}).length);
  return result;
}

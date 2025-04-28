// // assets/highlight_studies.js

// // Fonction pour appliquer le style basé sur les études filtrées
// function highlightStudies() {
//     // Récupérer les données du store
//     const storeElement = document.getElementById('studies-with-parameter-store');
//     if (!storeElement) return;
    
//     // Obtenir les données JSON
//     try {
//         const studiesData = JSON.parse(storeElement.textContent);
        
//         // Appliquer le style
//         document.querySelectorAll('.m_390b5f4').forEach(element => {
//             element.querySelectorAll('span').forEach(span => {
//                 if (studiesData.includes(span.textContent.trim())) {
//                     element.classList.add('style-special');
//                 } else {
//                     element.classList.remove('style-special');
//                 }
//             });
//         });
//     } catch (e) {
//         console.error("Error parsing studies data:", e);
//     }
// }

// // Observer les changements dans le store
// function observeStoreChanges() {
//     const storeObserver = new MutationObserver(highlightStudies);
//     const storeElement = document.getElementById('studies-with-parameter-store');
//     if (storeElement) {
//         storeObserver.observe(storeElement, { characterData: true, childList: true, subtree: true });
//     }
// }

// // Observer les changements dans le DOM pour trouver le store quand il sera ajouté
// const domObserver = new MutationObserver((mutations) => {
//     if (document.getElementById('studies-with-parameter-store')) {
//         highlightStudies();
//         observeStoreChanges();
//         domObserver.disconnect();
//     }
// });

// // Commencer l'observation
// document.addEventListener('DOMContentLoaded', () => {
//     if (document.getElementById('studies-with-parameter-store')) {
//         highlightStudies();
//         observeStoreChanges();
//     } else {
//         domObserver.observe(document.body, { childList: true, subtree: true });
//     }
    
//     // Observer également pour de nouveaux éléments .m_390b5f4 qui pourraient être ajoutés
//     const elementsObserver = new MutationObserver(highlightStudies);
//     elementsObserver.observe(document.body, { childList: true, subtree: true });
// });
// nav-include.js
document.addEventListener('DOMContentLoaded', () => {
    
    // --- Configuration ---
    const navItems = [
        { text: 'waste to fuel', href: 'waste.html' },
        { text: 'water to drink', href: 'water.html' },
        { text: 'cooking with sunshine', href: 'cook.html' },
    ];
    const languages = [
        { code: 'en', name: 'English', dir: 'ltr' }, 
        { code: 'es', name: 'Español', dir: 'ltr' },
        { code: 'fr', name: 'Français', dir: 'ltr' }, 
        { code: 'de', name: 'Deutsch', dir: 'ltr' },
        { code: 'zh', name: '中文', dir: 'ltr' }, 
        { code: 'ja', name: '日本語', dir: 'ltr' },
        { code: 'ru', name: 'Русский', dir: 'ltr' }, 
        { code: 'ar', name: 'العربية', dir: 'rtl' },
        { code: 'pt', name: 'Português', dir: 'ltr' }, 
        { code: 'hi', name: 'हिन्दी', dir: 'ltr' },
        { code: 'am', name: 'አማርኛ', dir: 'ltr' }
    ];
    const supportedLangCodes = languages.map(l => l.code);

    // --- Create Language Suggestion Modal ---
    const createLangSuggestionModal = () => {
        const modal = document.createElement('div');
        modal.id = 'lang-suggestion-modal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="lang-suggestion-title">
                <button class="modal-close-button" aria-label="Close dialog">&times;</button>
                <h2 id="lang-suggestion-title">Language Suggestion</h2>
                <p class="suggestion-message">We noticed your browser is set to a language we don't currently support.</p>
                <p>What content would you like to see translated? Your feedback helps us prioritize our efforts.</p>
                <textarea class="lang-suggestion-input" placeholder="For example: 'The section on solar cooking' or 'The donation process'"></textarea>
            </div>
        `;
        document.body.appendChild(modal);

        // Add event listeners for this new modal
        const closeBtn = modal.querySelector('.modal-close-button');
        closeBtn.addEventListener('click', () => modal.classList.remove('show'));
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.classList.remove('show');
            }
        });
    };
    createLangSuggestionModal();

    // --- Language Auto-Detection and Redirection Logic ---
    const performLanguageCheck = () => {
        if (sessionStorage.getItem('langCheckPerformed')) {
            return;
        }

        const userLang = navigator.language || navigator.userLanguage;
        const primaryLangCode = userLang.split('-')[0];

        // Only act if the current page is the root index.html
        const isHomePage = window.location.pathname.endsWith('/') || window.location.pathname.endsWith('index.html');
        
        if (isHomePage && primaryLangCode !== 'en' && !window.location.hash) {
            if (supportedLangCodes.includes(primaryLangCode)) {
                sessionStorage.setItem('langCheckPerformed', 'true');
                window.location.hash = primaryLangCode;
                window.location.reload();
            } else {
                const suggestionModal = document.getElementById('lang-suggestion-modal');
                if (suggestionModal) {
                    try {
                        const langName = new Intl.DisplayNames(['en'], { type: 'language' }).of(primaryLangCode);
                        const messageEl = suggestionModal.querySelector('.suggestion-message');
                        messageEl.textContent = `We noticed your browser is set to ${langName} (${primaryLangCode}), which we don't currently support.`;
                    } catch (e) {
                        console.warn("Could not display language name.", e);
                    }
                    suggestionModal.classList.add('show');
                }
            }
        }
        sessionStorage.setItem('langCheckPerformed', 'true');
    };

    // --- Language and Direction Handling ---
    const setPageLanguage = (langCode) => {
        const lang = languages.find(l => l.code === langCode);
        if (lang) {
            document.documentElement.lang = lang.code;
            document.documentElement.dir = lang.dir;
        }
    };

    const initialLang = window.location.hash.substring(1);
    if (initialLang && supportedLangCodes.includes(initialLang)) {
        setPageLanguage(initialLang);
    } else {
        const htmlLang = document.documentElement.lang;
        if (htmlLang && supportedLangCodes.includes(htmlLang)) {
            setPageLanguage(htmlLang);
        } else {
            setPageLanguage('en');
        }
    }

    // --- Header Rendering ---
    const headerContainer = document.getElementById('main-navigation');
    if (!headerContainer) {
        console.error("[Nav Error] Header target element with ID 'main-navigation' not found.");
        return;
    }
    // ... (The rest of the header rendering code remains the same)
    const currentPageFilename = document.body.dataset.currentPage || '';
    const containerDiv = document.createElement('div');
    containerDiv.className = 'header-container';
    const leftSection = document.createElement('div');
    leftSection.className = 'header-left';
    const logoDiv = document.createElement('div');
    logoDiv.className = 'header-logo';
    const logoLink = document.createElement('a');
    logoLink.href = 'index.html';
    logoLink.textContent = 'Appro-Connector';
    logoDiv.appendChild(logoLink);
    const navElement = document.createElement('nav');
    const ulElement = document.createElement('ul');
    navItems.forEach(item => {
        if (currentPageFilename.toLowerCase() !== item.href.toLowerCase()) {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = item.href;
            a.textContent = item.text;
            li.appendChild(a);
            ulElement.appendChild(li);
        }
    });
    navElement.appendChild(ulElement);
    leftSection.appendChild(logoDiv);
    leftSection.appendChild(navElement);
    const rightSection = document.createElement('div');
    rightSection.className = 'header-right-controls';
    const langSwitcherDiv = document.createElement('div');
    langSwitcherDiv.className = 'language-switcher';
    const langButton = document.createElement('button');
    langButton.className = 'lang-button';
    langButton.innerHTML = `<svg class="globe-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418" /></svg><span>Language</span>`;
    const langDropdown = document.createElement('ul');
    langDropdown.className = 'language-dropdown';
    languages.forEach(lang => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#${lang.code}`;
        a.textContent = lang.name;
        a.dataset.lang = lang.code;
        li.appendChild(a);
        langDropdown.appendChild(li);
    });
    langSwitcherDiv.appendChild(langButton);
    langSwitcherDiv.appendChild(langDropdown);
    const donateButton = document.createElement('button');
    donateButton.className = 'donate-button';
    donateButton.textContent = 'Donate';
    rightSection.appendChild(langSwitcherDiv);
    rightSection.appendChild(donateButton);
    containerDiv.appendChild(leftSection);
    containerDiv.appendChild(rightSection);
    headerContainer.innerHTML = '';
    headerContainer.appendChild(containerDiv);

    // --- Donation Modal Creation and Listeners ---
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    modalOverlay.innerHTML = `
        <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <button class="modal-close-button" aria-label="Close dialog">&times;</button>
            <h2 id="modal-title">Support Our Work</h2>
            <p>Your contribution helps us continue our mission to create sustainable solutions for communities worldwide. Thank you for your generosity!</p>
        </div>
    `;
    document.body.appendChild(modalOverlay);
    const modalCloseButton = modalOverlay.querySelector('.modal-close-button');
    donateButton.addEventListener('click', () => {
        modalOverlay.classList.add('show');
        modalCloseButton.focus();
    });
    const closeModal = () => {
        modalOverlay.classList.remove('show');
        donateButton.focus();
    };
    modalCloseButton.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (event) => {
        if (event.target === modalOverlay) closeModal();
    });
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modalOverlay.classList.contains('show')) closeModal();
    });

    // --- Language Switcher Listeners ---
    langButton.addEventListener('click', (event) => {
        event.stopPropagation();
        langDropdown.classList.toggle('show');
    });
    langDropdown.addEventListener('click', (event) => {
        if (event.target.dataset.lang) {
            window.location.hash = event.target.dataset.lang;
            window.location.reload();
        }
    });
    window.addEventListener('click', (event) => {
        if (!langSwitcherDiv.contains(event.target)) {
            langDropdown.classList.remove('show');
        }
    });

    // --- Run the initial language check ---
    performLanguageCheck();
});


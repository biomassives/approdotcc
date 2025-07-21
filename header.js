// /header.js

// --- CONFIGURATION ---
// IMPORTANT: Change this to your project's GitHub repository URL.
const GITHUB_REPO_URL = 'https://github.com/your-username/your-repo';

const availableLanguages = [
    { code: 'en', name: 'English', folder: '/' },
    { code: 'es', name: 'Español', folder: '/es/' },
    { code: 'sw', name: 'Kiswahili', folder: '/sw/' },
    { code: 'ar', name: 'العربية', folder: '/ar/' },
    { code: 'uk', name: 'Українська', folder: '/uk/' },
    { code: 'am', name: 'አማርኛ', folder: '/am/' }
];
// --------------------

class SmartHeader {
    constructor(elementId) {
        this.headerElement = document.getElementById(elementId);
        if (!this.headerElement) {
            console.error('SmartHeader Error: Element with ID "' + elementId + '" not found.');
            return;
        }
        this.currentLang = this.getCurrentLanguage();
        this.handleLanguageRedirect();
        this.render();
    }

    /**
     * Determines the language of the current page from the URL path.
     */
    getCurrentLanguage() {
        const path = window.location.pathname;
        const langConfig = availableLanguages.find(lang => path.startsWith(lang.folder) && lang.folder !== '/');
        return langConfig ? langConfig.code : 'en';
    }

    /**
     * Checks browser language and redirects if a supported version exists and it's the user's first visit.
     */
    handleLanguageRedirect() {
        // Stop if a redirect decision has already been made in this session.
        if (sessionStorage.getItem('lang_redirect_handled')) {
            return;
        }

        const browserLang = navigator.language.split('-')[0]; // 'es-CR' -> 'es'
        const supportedLang = availableLanguages.find(lang => lang.code === browserLang);

        // Mark as handled so this logic doesn't run again in this session.
        sessionStorage.setItem('lang_redirect_handled', 'true');

        if (supportedLang && supportedLang.code !== this.currentLang) {
            // Redirect to the appropriate language folder.
            window.location.href = supportedLang.folder;
        } else if (!supportedLang) {
            // If the language is not supported at all, show the contribution popup.
            this.showContributePopup(browserLang);
        }
    }

    /**
     * Renders the header HTML including the language switcher.
     */
    render() {
        const isRtl = this.currentLang === 'ar';
        const textAlign = isRtl ? 'text-right' : 'text-left';
        const headerClasses = isRtl ? 'bg-orange-600' : 'bg-blue-600'; // Example: different color for RTL

        let dropdownHTML = '';
        availableLanguages.forEach(lang => {
            dropdownHTML += `
                <a href="${lang.folder}" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">${lang.name}</a>
            `;
        });

        const headerHTML = `
            <div class="header flex flex-col items-start ${headerClasses} text-white p-4 shadow-md">
                <div class="w-full flex justify-between items-center">
                    <div class="logo flex items-start">
                        <h1 class="text-xl font-bold"><a href=/>Appro Community Connector</a></h1>
                    </div>
                    <div id="language-switcher" class="relative">
                        <button class="flex items-center p-2 border border-white rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10 2a8 8 0 015.932 13.342l-2.66-2.66A5 5 0 105.33 9.332L2.658 12.005A8 8 0 0110 2zm.001 16a8 8 0 01-5.932-13.342l2.66 2.66A5 5 0 1014.67 10.668l2.662-2.662A8 8 0 0110.001 18z" />
                            </svg>
                            <span>Language</span>
                        </button>
                        <div class="dropdown-content absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 hidden">
                            ${dropdownHTML}
                        </div>
                    </div>
                </div>
                <nav class="breadcrumbs w-full ${textAlign} mt-2">
                    </nav>
            </div>
        `;
        this.headerElement.innerHTML = headerHTML;
        this.addEventListeners();
    }
    
    /**
     * Creates and displays a popup for language contribution.
     */
    showContributePopup(langCode) {
        const modalHTML = `
            <div id="contribute-modal" class="modal-overlay">
                <div class="modal-content">
                    <button id="close-modal" class="absolute top-2 right-4 text-2xl font-bold">&times;</button>
                    <h2 class="text-2xl font-bold mb-4">Help Us Translate!</h2>
                    <p class="mb-4">It looks like your browser is set to <strong>${langCode}</strong>, a language we don't have yet. Would you be interested in helping us create a new version?</p>
                    <p class="mb-6 text-sm text-gray-600">By submitting, you'll open a new, pre-filled GitHub Issue. No coding required!</p>
                    <form id="contribute-form">
                        <div class="mb-4">
                            <label for="lang-name" class="block text-sm font-medium text-gray-700">Language Name (e.g., French)</label>
                            <input type="text" id="lang-name" name="lang-name" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" required>
                            <input type="hidden" id="lang-code" name="lang-code" value="${langCode}">
                        </div>
                        <button type="submit" class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700">Contribute New Language</button>
                    </form>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Event Listeners for the modal
        document.getElementById('close-modal').addEventListener('click', () => {
            document.getElementById('contribute-modal').remove();
        });

        document.getElementById('contribute-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const langName = document.getElementById('lang-name').value;
            const issueTitle = encodeURIComponent(`Language Request: Add ${langName} (${langCode})`);
            const issueBody = encodeURIComponent(
`**New Language Translation Request**

* **Language Name:** ${langName}
* **Language Code:** \`${langCode}\`

**Action for Maintainer:**
1.  Create a new folder: \`/${langCode}/\`
2.  Copy \`/index.html\` to the new folder.
3.  Copy relevant assets (images, av) or create placeholders.
4.  Begin translation of \`/${langCode}/index.html\`.
5.  Add the new language to the \`availableLanguages\` array in \`header.js\`.

Thank you for contributing!
`
            );
            
            const githubUrl = `${GITHUB_REPO_URL}/issues/new?title=${issueTitle}&body=${issueBody}`;
            window.open(githubUrl, '_blank');
            document.getElementById('contribute-modal').remove();
        });
    }

    /**
     * Adds event listeners for the language switcher dropdown.
     */
    addEventListeners() {
        const switcher = document.getElementById('language-switcher');
        const dropdown = switcher.querySelector('.dropdown-content');

        switcher.addEventListener('click', (event) => {
            event.stopPropagation();
            dropdown.classList.toggle('hidden');
        });

        document.addEventListener('click', () => {
            if (!dropdown.classList.contains('hidden')) {
                dropdown.classList.add('hidden');
            }
        });
    }
}

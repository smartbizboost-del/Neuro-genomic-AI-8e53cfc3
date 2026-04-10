(function () {
    function normalizeBase(url) {
        return String(url || '').replace(/\/$/, '');
    }

    window.getNGAIApiBaseUrl = function () {
        if (window.NGAI_API_BASE_URL) {
            return normalizeBase(window.NGAI_API_BASE_URL);
        }

        if (window.location && window.location.protocol && window.location.protocol !== 'file:') {
            return normalizeBase(`${window.location.origin}/api/v1`);
        }

        return 'http://localhost:8000/api/v1';
    };

    window.getNGAIApiUrl = function (path) {
        const cleanPath = String(path || '').startsWith('/') ? String(path || '') : `/${path || ''}`;
        return `${window.getNGAIApiBaseUrl()}${cleanPath}`;
    };
})();
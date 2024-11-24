// API 엔드포인트 설정
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// API 호출 유틸리티 함수
async function callApi(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API 호출 중 오류가 발생했습니다.');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API 호출 오류:', error);
        throw error;
    }
}

// 인증 관련 함수들
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// 로딩 상태 관리
function showLoading() {
    const loader = document.querySelector('.loading-overlay');
    if (loader) loader.style.display = 'flex';
}

function hideLoading() {
    const loader = document.querySelector('.loading-overlay');
    if (loader) loader.style.display = 'none';
}

// 에러 메시지 표시
function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

// 기존 코드에 추가
class APIError extends Error {
    constructor(message, status) {
        super(message);
        this.name = 'APIError';
        this.status = status;
    }
}

async function handleAPIError(error) {
    console.error('API Error:', error);
    
    if (error instanceof APIError) {
        if (error.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
            return;
        }
        showError(error.message);
    } else {
        showError('알 수 없는 오류가 발생했습니다.');
    }
} 
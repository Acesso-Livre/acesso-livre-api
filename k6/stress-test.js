import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

// Teste de Stress: encontra o ponto de quebra da API
export const options = {
    stages: [
        { duration: '30s', target: 50 },
        { duration: '30s', target: 100 },
        { duration: '30s', target: 200 },
        { duration: '30s', target: 300 },  // Acima do solicitado para encontrar limite
        { duration: '30s', target: 400 },
        { duration: '1m', target: 0 },     // Recovery
    ],
    thresholds: {
        http_req_duration: ['p(99)<5000'], // Mais tolerante para stress test
    },
};

const BASE_URL = 'https://acesso-livre-api.onrender.com';

export default function () {
    const res = http.get(`${BASE_URL}/api/locations/`);

    check(res, {
        'status is 200': (r) => r.status === 200,
        'response time < 2s': (r) => r.timings.duration < 2000,
    });

    errorRate.add(res.status !== 200);

    sleep(0.3);
}

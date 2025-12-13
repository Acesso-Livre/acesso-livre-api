import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('errors');
const locationsTrend = new Trend('locations_duration');
const commentsTrend = new Trend('comments_duration');

// Configuração do teste
export const options = {
    stages: [
        { duration: '30s', target: 50 },   // Ramp-up para 50 VUs
        { duration: '1m', target: 200 },   // Ramp-up para 200 VUs
        { duration: '2m', target: 200 },   // Mantém 200 VUs por 2 minutos
        { duration: '30s', target: 0 },    // Ramp-down
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'], // 95% das requests < 2s
        errors: ['rate<0.1'],              // Taxa de erro < 10%
    },
};

const BASE_URL = 'https://acesso-livre-api.onrender.com';

// Endpoints públicos para teste
const endpoints = {
    locations: `${BASE_URL}/api/locations/`,
    accessibilityItems: `${BASE_URL}/api/locations/accessibility-items/`,
    recentComments: `${BASE_URL}/api/comments/recent`,
    commentIcons: `${BASE_URL}/api/comments/icons/`,
};

export default function () {
    // 1. Listar localizações
    const locationsRes = http.get(endpoints.locations);
    locationsTrend.add(locationsRes.timings.duration);
    check(locationsRes, {
        'locations status 200': (r) => r.status === 200,
        'locations has data': (r) => {
            try {
                const body = JSON.parse(r.body);
                return body.locations !== undefined;
            } catch {
                return false;
            }
        },
    });
    errorRate.add(locationsRes.status !== 200);

    sleep(0.5);

    // 2. Buscar itens de acessibilidade
    const accessibilityRes = http.get(endpoints.accessibilityItems);
    check(accessibilityRes, {
        'accessibility items status 200': (r) => r.status === 200,
    });
    errorRate.add(accessibilityRes.status !== 200);

    sleep(0.5);

    // 3. Comentários recentes
    const recentCommentsRes = http.get(endpoints.recentComments);
    commentsTrend.add(recentCommentsRes.timings.duration);
    check(recentCommentsRes, {
        'recent comments status 200': (r) => r.status === 200,
    });
    errorRate.add(recentCommentsRes.status !== 200);

    sleep(0.5);

    // 4. Ícones de comentários
    const iconsRes = http.get(endpoints.commentIcons);
    check(iconsRes, {
        'comment icons status 200': (r) => r.status === 200,
    });
    errorRate.add(iconsRes.status !== 200);

    sleep(0.5);

    // 5. Buscar localização específica (se existir alguma)
    try {
        const locationsData = JSON.parse(locationsRes.body);
        if (locationsData.locations && locationsData.locations.length > 0) {
            const randomLocation = locationsData.locations[Math.floor(Math.random() * locationsData.locations.length)];
            const locationDetailRes = http.get(`${BASE_URL}/api/locations/${randomLocation.id}`);
            locationsTrend.add(locationDetailRes.timings.duration);
            check(locationDetailRes, {
                'location detail status 200': (r) => r.status === 200,
            });
            errorRate.add(locationDetailRes.status !== 200);

            // 6. Buscar comentários dessa localização
            const commentsRes = http.get(`${BASE_URL}/api/comments/${randomLocation.id}/comments`);
            commentsTrend.add(commentsRes.timings.duration);
            check(commentsRes, {
                'location comments status 200': (r) => r.status === 200,
            });
            errorRate.add(commentsRes.status !== 200);
        }
    } catch (e) {
        // Ignora erros de parsing
    }

    sleep(1);
}

// Função executada ao final do teste
export function handleSummary(data) {
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'k6/summary.json': JSON.stringify(data, null, 2),
    };
}

function textSummary(data, options) {
    const { metrics } = data;

    let summary = '\n========== RESUMO DO TESTE DE CARGA ==========\n\n';

    summary += `Total de Requisições: ${metrics.http_reqs?.values?.count || 0}\n`;
    summary += `Duração Média: ${(metrics.http_req_duration?.values?.avg || 0).toFixed(2)}ms\n`;
    summary += `P95: ${(metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2)}ms\n`;
    summary += `Taxa de Erro: ${((metrics.errors?.values?.rate || 0) * 100).toFixed(2)}%\n`;

    summary += '\n===============================================\n';

    return summary;
}

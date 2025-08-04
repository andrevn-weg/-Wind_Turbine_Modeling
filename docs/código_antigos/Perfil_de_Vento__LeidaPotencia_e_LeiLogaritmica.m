clc
clear all
close all
 
 %Lei de Potência - Ganho da Velocidade do Vento com a Altura
 
% Parametros Iniciais
V_referencia = 2.7; % velocidade do vento na altura de referência (medida)
H_referencia = 10; %  altura de referência

% Parametros Desejados
%V_desejado = 30; % velocidade do vento na altura (H)
%H_desejado = 50; % altura desejada
H_desejado = 0:0.1:100;

n = 0.22;
% Valores de n:
% Superfície lisa, lago ou oceano 0,10
% Grama baixa 0,14
% Vegetação rasteira (até 0,3m), árvores ocasionais 0,16
% Arbustos, árvores ocasionais 0,20
% Árvores, construções ocasionais 0,22 – 0,24
% Áreas residenciais 0,28 – 0,40
% Cálculo da Lei de Potência (vetorizado)
V_desejado_LP = V_referencia * (H_desejado / H_referencia).^n;


% Lei logarítmica
z0 = 150 / 1000; 
% DESCRIÇÃO DO TERRENO z0 (mm)
% Liso, gelo, lama 0,01
% Mar aberto e calmo 0,20
% Mar agitado 0,50
% Neve 3,00
% Gramado 8,00
% Pasto acidentado 10,00
% Campo em declive 30,00
% Cultivado 50,00
% Poucas árvores 100,00
% Muitas árvores, poucos edifícios, cercas 250,00
% Florestas 500,00
% Subúrbios 1.500,00
% Zonas urbanas com edifícios altos 3.000,00


% Cálculo da Lei Logarítmica (vetorizado)
V_desejado_LG = V_referencia * log(H_desejado/z0) / log(H_referencia/z0);


% Encontrar ponto de intersecção das curvas
diff_curves = abs(V_desejado_LP - V_desejado_LG);
[~, idx_intersect] = min(diff_curves);
h_intersect = H_desejado(idx_intersect);
v_intersect = V_desejado_LP(idx_intersect);

% Pontos a cada 10 metros (otimizado)
alturas_destaque = 10:10:100;
% Interpolar valores nas alturas de destaque
velocidades_LP_destaque = interp1(H_desejado, V_desejado_LP, alturas_destaque, 'linear');
velocidades_LG_destaque = interp1(H_desejado, V_desejado_LG, alturas_destaque, 'linear');

% Plotando os gráficos
figure('Position', [100, 100, 900, 600]);
hold on;

% Plotar as curvas principais
plot(H_desejado, V_desejado_LP, 'b-', 'LineWidth', 2, 'DisplayName', 'Lei de Potência');
plot(H_desejado, V_desejado_LG, 'r-', 'LineWidth', 2, 'DisplayName', 'Lei Logarítmica');

% Destacar pontos a cada 10 metros
plot(alturas_destaque, velocidades_LP_destaque, 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'b', 'HandleVisibility', 'off');
plot(alturas_destaque, velocidades_LG_destaque, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r', 'HandleVisibility', 'off');

% Destacar ponto de intersecção
plot(h_intersect, v_intersect, 'ko', 'MarkerSize', 12, 'MarkerFaceColor', 'yellow', 'MarkerEdgeColor', 'black', 'LineWidth', 2, 'DisplayName', sprintf('Intersecção (%.1fm, %.2fm/s)', h_intersect, v_intersect));

% Adicionar anotações para pontos a cada 10 metros
for i = 1:length(alturas_destaque)
    % Anotações para Lei de Potência
    text(alturas_destaque(i), velocidades_LP_destaque(i) + 0.1, ...
         sprintf('%.1fm/s', velocidades_LP_destaque(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 8, 'Color', 'blue', 'FontWeight', 'bold');
    
    % Anotações para Lei Logarítmica
    text(alturas_destaque(i), velocidades_LG_destaque(i) - 0.15, ...
         sprintf('%.1fm/s', velocidades_LG_destaque(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 8, 'Color', 'red', 'FontWeight', 'bold');
end

% Adicionar linha vertical no ponto de intersecção
line([h_intersect, h_intersect], [0, v_intersect], 'Color', 'k', 'LineStyle', '--', 'LineWidth', 1, 'HandleVisibility', 'off');

% Configurações do gráfico
title('Perfil de Vento: Lei de Potência vs Lei Logarítmica', 'FontSize', 14, 'FontWeight', 'bold');
xlabel('Altura (m)', 'FontSize', 12);
ylabel('Velocidade do Vento (m/s)', 'FontSize', 12);
legend('Location', 'southeast', 'FontSize', 10);
grid on;
grid minor;

% Configurar eixos
xlim([0, 100]);
ylim([0, max([max(V_desejado_LP), max(V_desejado_LG)]) * 1.1]);

% Adicionar informações dos parâmetros no gráfico
text(5, max([max(V_desejado_LP), max(V_desejado_LG)]) * 0.9, ...
     sprintf('Parâmetros:\nV_{ref} = %.1f m/s\nH_{ref} = %d m\nn = %.2f\nz_0 = %.3f m', ...
     V_referencia, H_referencia, n, z0), ...
     'FontSize', 9, 'BackgroundColor', 'white', 'EdgeColor', 'black');

% Exibir tabela com valores dos pontos destacados
fprintf('\n========== RESULTADOS ==========\n');
fprintf('Ponto de Intersecção: %.1f m - %.2f m/s\n\n', h_intersect, v_intersect);
fprintf('Valores a cada 10 metros:\n');
fprintf('Altura (m) | Lei Potência (m/s) | Lei Logarítmica (m/s) | Diferença (m/s)\n');
fprintf('-----------|-------------------|---------------------|----------------\n');
for i = 1:length(alturas_destaque)
    diff_value = abs(velocidades_LP_destaque(i) - velocidades_LG_destaque(i));
    fprintf('%8.0f   |      %6.2f       |       %6.2f        |     %6.3f\n', ...
            alturas_destaque(i), velocidades_LP_destaque(i), velocidades_LG_destaque(i), diff_value);
end
fprintf('================================\n');

% Melhorar aparência
set(gca, 'FontSize', 10);
box on;
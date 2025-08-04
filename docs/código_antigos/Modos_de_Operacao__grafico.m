clc
close all
clear all
% Dados do gráfico
v_cut_in = 2.3; % Velocidade de corte inicial (m/s)
v_nom = 9; % Velocidade nominal (m/s)
v_cut_out = 20; % Velocidade de corte final (m/s)
P_nom = 24000; % Potência nominal (kW)

% Vetores de velocidade e potência
velocidade = [0 v_cut_in v_nom v_cut_out v_cut_out];
potencia = [0 0 P_nom P_nom 0];

% Plot do gráfico
figure;
plot(velocidade, potencia, 'b', 'LineWidth', 1);
hold on;

% Adicionando anotações ao gráfico
text(1, 400, 'PARADO', 'HorizontalAlignment', 'center', 'FontSize', 10);
%text(v_cut_in+0.5, 1000, 'v_{cut-in}', 'HorizontalAlignment', 'center', 'FontSize', 14);
text(v_cut_in+4, 14000, 'MPPT', 'HorizontalAlignment', 'center', 'FontSize', 14);
%text(v_nom+0.5, P_nom - 1000, 'v_{nominal}', 'HorizontalAlignment', 'center', 'FontSize', 14);
text(v_nom+5, P_nom + 1000, 'Potência Nominal', 'HorizontalAlignment', 'center', 'FontSize', 14);
%text(v_cut_out, 1500, 'v_{cut-off}', 'HorizontalAlignment', 'center', 'FontSize', 14);



% Configurações do gráfico
xlabel('Velocidade (m/s)');
ylabel('Potência (kW)');
title('Regiões de Operação de uma Turbina Eólica');
grid on;
axis([0 21 0 30000]);

hold off;

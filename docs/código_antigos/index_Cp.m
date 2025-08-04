% Inicialize a classe com valores específicos
model = WindTurbineModel;
model.raio_pas_aerogerador = 50;   % Defina o raio das pás do rotor em metros
model.velocidade_vento = 12;       % Defina a velocidade do vento em m/s

% Exemplo 1: Chamar Model_Cp com valores específicos para beta e omega
beta = 0;       % Ângulo de passo das pás
omega = 2.5;    % Velocidade angular do rotor em rad/s
c1 = 0.5; c2 = 116; c3 = 0.4; c4 = 0; c5 = 0; c6 = 5; c7 = 21; c8 = 0.08; c9 = 0.035; % Não precisa mexer

[Cp, lamb_i, lamb] = model.Model_Cp(model.velocidade_vento, beta, omega, c1, c2, c3, c4, c5, c6, c7, c8, c9);
disp(['Cp = ', num2str(Cp), ', lambda_i = ', num2str(lamb_i), ', lambda = ', num2str(lamb)]);

% Exemplo 2: Chamar Cp_Heier, que usa parâmetros fixos
[Cp, lamb_i, lamb] = model.Cp_Heier(model.velocidade_vento, beta, omega);
disp(['Cp (Heier) = ', num2str(Cp), ', lambda_i = ', num2str(lamb_i), ', lambda = ', num2str(lamb)]);

function N = countlanes(mot, ilanes, iLPF, minv)
%% countlanes  count automobiles in each lane
%
%%% inputs
% * mot: 2-D image of motion magnitude
% * ilanes: N x 2 pixel "upper / lower" boundaries for each lane
% * iLPF: spatial low pass filter indices
% * minv: power detection threshold

%% sanity check
validateattributes(mot, {'numeric'}, {'real', '2d'})
validateattributes(ilanes, {'numeric'}, {'real', 'nonnegative', 'size', [NaN, 2]})
validateattributes(iLPF, {'numeric'}, {'real', 'numel', 2})
validateattributes(minv, {'numeric'}, {'real', 'scalar', 'nonnegative'})

Nlanes = size(ilanes(1));
%% for each lane, count automobiles
% Automobile are big and move fast usually, staying in the same lane
% typically in the field of view.
N = 0;
for i = 1:Nlanes
%% average over lane width
  lane = sum(mot(ilanes(i,1):ilanes(i,2), :), 1);
%% compute spatial spectral power
  Flane = fftshift(abs(fft(lane)).^2);
%% integrate low frequency power
  M = sum(Flane(iLPF(1):iLPF(2)));
%% if low frequency signal is strong enough, declare detection
  N = N + minv <= M;
end

end

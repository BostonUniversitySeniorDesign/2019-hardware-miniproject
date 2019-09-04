function CountMotion(h5fn, key)
%% CountMotion  load motion data and count vehicles
%
%%% inputs
% * h5fn: HDF5 filename
% * key: HDF5 variable with desired data
%

validateattributes(h5fn, {'string','char'}, {'vector'})
validateattributes(key, {'string','char'}, {'vector'})
%% load motion data
assert(exist(h5fn,'file')==2, [h5fn, ' does not exist'])

if isoctave
  motion = load(h5fn, key);
else % matlab
  motion = h5read(h5fn, key);
end
motion = motion.(key);

%% lane geometry parameters, empirical based on camera perspective w.r.t. traffic

ilanes = [25, 27;
          35, 40];

L = size(motion, 2);
iLPF = [round(L*4/9), round(L*5/9)];

minv = 500;

%% main loop -- 60 fps on Pi Zero !
Ncount = 0;
Nframe = size(motion, 3);
tic
for i = 1:Nframe
  N = countlanes(motion(:,:,i), ilanes, iLPF, minv);
  Ncount = Ncount + N;
end

disp(['processed output at ', num2str(Nframe / toc, '%0.1f'), ' fps.'])

end


function N = countlanes(mot, ilanes, iLPF, minv)
%% countlanes  count automobiles in each lane
%
%%% inputs
% * mot: 2-D image of motion magnitude
% * ilanes: N x 2 pixel "upper / lower" boundaries for each lane
% * iLPF: spatial low pass filter indices
% * minv: power detection threshold

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

cwd = fileparts(mfilename('fullpath'));

%% car test
assert(sum(CountMotion([cwd, filesep, 'data/motion.h5'], 'dxdy')) == 142)

%% hand test
N = sum(CountMotion([cwd, filesep, 'data/motion_hand.h5'], {'dx', 'dy'}));
assert(N == 18, [int2str(N), ' != 18'])

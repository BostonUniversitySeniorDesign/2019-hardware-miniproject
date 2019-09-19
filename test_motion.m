cwd = fileparts(mfilename('fullpath'));

assert(sum(CountMotion([cwd, filesep, 'data/motion.h5'], 'dxdy')) == 142)
%% Multi-lane automobile detection
% This project runs at ~ 100 fps on the Pi Zero.
% The enormous speed comes from using the GPU to do the hardest parts:
% resizing and optical flow computation.
%
% * <countlanes.html countlanes>
% * <docount.html docount>
% * <motdet.html motdet>


function publish_all(path)

flist = dir([path, filesep, '*.m']);

for i = 1:length(flist)
  fn = publish([path,filesep,flist(i).name], 'evalCode', false, 'outputDir', 'docs');
  [~,fname,ext] = fileparts(fn);
  fn = [fname, ext];
  
  disp(['% * <',fn,' ',fname,'>'])
end


end
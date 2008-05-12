function prop=linespec2prop(spec)
% LINESPEC2PROP  Convert PLOT style line specs to properties
%  PROPR = LINESPEC2PROP(SPEC) converts the string SPEC to a cell
%  array of properties PROPR. SPEC is in the format of PLOT().
%
%  If SPEC is not in a recognized format, the string SPEC is returned
%  unaltered as the only element of PROPR.
%
%  See also PLOT(), VLFEAT.

% AUTORIGHTS
% Copyright 2007 (c) Andrea Vedaldi and Brian Fulkerson
% 
% This file is part of VLFeat, available in the terms of the GNU
% General Public License version 2.

prop = {} ;

if ~ ischar(spec)
  error('SPEC must be a string') ;
end

spec_ = spec ;

switch spec(1:min(numel(spec),1))
  case {'b' 'g' 'r' 'c' 'm' 'y' 'k' 'w'}
    prop = {prop{:}, 'Color', spec(1)} ;
    spec(1) = [] ;
end

switch spec(1:min(numel(spec),1))
  case {'.' 'o' 'x' '+' '*' 's' 'd' 'v' '^' '<' '>' 'p' 'h'}
    prop = {prop{:}, 'Marker', spec(1)} ;
    spec(1) = [] ;
end

if isempty(spec)
  return ;
end

switch spec
  case {'-' ':' '-.' '--'}
    prop = {prop{:}, 'LineStyle', spec} ;
  otherwise
    prop = {spec_} ;
end

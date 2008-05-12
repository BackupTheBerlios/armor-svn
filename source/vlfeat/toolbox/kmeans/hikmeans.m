function [tree,asgn] = hikmeans(data,K,nleaves)
% HIKMEANS  Hierachical integer K-means
%   [TREE,ASGN] = HIKMENAS(DATA,K,NLEAVES) applies recursive integer
%   K-menas to cluster the data DATA, returing a structure TREE
%   representing the clusters and a vector ASGN with the data to
%   cluster assignments. The depth of the recursive partition is
%   computed so that at least NLEAVES are generated.
%
%   HIKMEANS() is built on top of IKMEANS() and requires the data to
%   be of class UINT8.
%
%   TREE is a structure representing the hierarchical clusters.  Each
%   node of the tree is also a structure with fields:
%   
%   .DEPTH    Depth of the tree (only at the root node)
%   .CENTERS  K cluster centers
%   .SUB      Array of K node structures representing subtrees 
%             (this field is missing at leaves).
%
%   ASGN is a matrix with one column per datum and height equal to the
%   depth of the tree. Each column encodes the branch of the tree that
%   correspond to each datum.
%
%   Examples:
%
%     ASGN(:,7) = [1 5 3] means that the tree as depth equal to 3 and
%     that the datum X(:,7) corresponds to the branch
%     ROOT->SUB(1)->SUB(5)->SUB(3).

% AUTORIGHTS
% Copyright 2007 (c) Andrea Vedaldi and Brian Fulkerson
% 
% This file is part of VLFeat, available in the terms of the GNU
% General Public License version 2.

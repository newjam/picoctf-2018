{-# LANGUAGE DeriveFunctor #-}
{-# LANGUAGE TypeSynonymInstances #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE OverlappingInstances  #-}

import Text.ParserCombinators.ReadP
import Data.Maybe

import System.Environment
import System.Exit


main = getArgs >>= parse

parse [e] = solve e
parse _   = usage >> exitSuccess

usage = do
  program <- getProgName
  putStrLn $ "Usage: " ++ program ++ " <expression>"
  putStrLn $ "Example: " ++ program ++ " \"() + (())\""

solve e = case (evaluate . read) e of
  Just t  -> (putStrLn . show) t >> exitSuccess
  Nothing -> putStrLn "Error!" >> exitFailure

-- Types

data Term = Empty | Contain Term | Combine Term Term
  deriving Eq

type Expression = [Term]

-- Utility

singleton = Contain Empty

height Empty     = 0
height (Contain t)   = 1 + height t
height (Combine l r) = max (height l) (height r)

rightmost (Combine _ r) = rightmost r
rightmost x             = x

leftmost (Combine l _) = l
leftmost x             = x

-- Rules

combine l r = if height l == height r then Just (Combine l r) else Nothing

absorb_right (Contain t) r =
  if height t >= height r
    then Just $ Contain (Combine t r)
    else Nothing
absorb_right _ _ = Nothing

absorb_left l (Contain t) =
  if height t >= height l
    then Just $ Contain (Combine l t)
    else Nothing
absorb_left _ _ = Nothing

-- TODO

combined_absorb_right (Combine t l) r = do
  l' <- absorb_right l r
  return (Combine t l')
combined_absorb_right _ _ = Nothing

combined_absorb_left  l (Combine r t) = do
  r' <- absorb_left l r
  return (Combine r' t)
combined_absorb_left  l r = Nothing

absorb_combined_right _ _ = Nothing
absorb_combined_left _ _ = Nothing

-- Evaluating Expression

add Empty r = Just r
add l Empty = Just l
add l r =
  if length attempts > 0
    then (Just . head) attempts
    else Nothing
  where
    attempts = catMaybes $ applyRules l r


applyRules l r = [
    combine l r,
    absorb_left l r,
    absorb_right l r,
    combined_absorb_right l r,
    combined_absorb_left l r,
    absorb_combined_right l r,
    absorb_combined_left l r
  ]


evaluate :: Expression -> Maybe Term
evaluate = foldl add' (Just Empty)
  where
    add' (Just x) y = add x y
    add' Nothing  _ = Nothing

-- Reading and Writing

instance Show Term where
  show Empty         = ""
  show (Contain t)   = "(" ++ show t ++ ")"
  show (Combine l r) = show l ++ show r

instance Read Term where
  readsPrec _ = readP_to_S parseTerm

parseTerm = parseContain +++ parseSingleton +++ parseCombine
parseContain = Contain <$> paren parseTerm
parseSingleton = string "()" >> return singleton
parseCombine = Combine <$> parseTermExceptCombine <*> parseTerm
parseTermExceptCombine =(parseSingleton +++ parseContain)
paren = between (char '(') (char ')')

instance Show Expression where
  show = foldr1 (\x y -> x ++ " + " ++ y) . map show

instance Read Expression where
  readsPrec _ = readP_to_S parseExpression

parseExpression = sepBy1 parseTerm (string " + ")

-- Tests

test_input1 = "(()) + (()()) + (()(())) + (()()) + ()() + (()()) + (()) + ()()() + ((())()) + ()"



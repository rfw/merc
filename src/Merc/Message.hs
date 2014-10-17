module Merc.Message (
  sendMessage,
  errNeedMoreParams,
  errErroneousNickname,
  rplWelcome,
  rplYourHost,
  rplCreated
) where

import Control.Concurrent.STM
import Data.Maybe
import Data.Monoid
import qualified Data.Text as T
import qualified Data.Text.IO as T
import Data.Time.Format
import Data.Version
import Merc.Emitter
import qualified Merc.Types.Message as M
import qualified Merc.Types.Server as S
import qualified Merc.Types.User as U
import Network
import Paths_merc (version)
import System.Locale
import System.Log.Logger

newServerMessage :: S.Server -> M.Command -> [T.Text] -> M.Message
newServerMessage S.Server{..} command params = M.Message {
  M.prefix = Just $ M.ServerPrefix serverName,
  M.command = command,
  M.params = params
}

newReplyMessage :: S.Client -> S.Server -> M.Command -> [T.Text] -> STM M.Message
newReplyMessage S.Client{..} server command params = do
  U.User{U.hostmask = U.Hostmask{U.nickname = nickname}} <- readTVar user
  return $ newServerMessage server command ((U.showNickname nickname):params)

sendMessage :: S.Client -> M.Message -> IO ()
sendMessage S.Client{..} message = do
  debugM "Merc.Message" $ "Sending message: " ++ show message
  T.hPutStrLn handle $ emitMessage message

errNeedMoreParams :: S.Client -> S.Server -> M.Command -> STM M.Message
errNeedMoreParams client server command =
  newReplyMessage client server M.ErrNeedMoreParams [commandName,
                                                     "Not enough parameters"]

  where
    commandName = fromJust $ M.getCommandName command

errErroneousNickname :: S.Client -> S.Server -> STM M.Message
errErroneousNickname client server = do
  newReplyMessage client server M.ErrErroneousNickname ["Erroneous nickname"]

rplWelcome :: S.Client -> S.Server -> STM M.Message
rplWelcome client@S.Client{..} server@S.Server{..} = do
  U.User{U.hostmask = U.Hostmask{U.nickname = nickname}} <- readTVar user

  newReplyMessage client server M.RplWelcome ["Welcome to the " <>
                                              networkName <>
                                              " Internet Rely Chat Network " <>
                                              U.showNickname nickname]

rplYourHost :: S.Client -> S.Server -> STM M.Message
rplYourHost client server@S.Server{..} =
  newReplyMessage client server M.RplYourHost ["Your host is " <> serverName <>
                                               ", running mercd-" <>
                                               T.pack (showVersion version)]

rplCreated :: S.Client -> S.Server -> STM M.Message
rplCreated client server@S.Server{..} =
  newReplyMessage client server M.RplCreated [
    "This server was created " <> T.pack (formatTime defaultTimeLocale "%c"
                                                     creationTime)]

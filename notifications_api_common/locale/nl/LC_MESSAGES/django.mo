��    )      d  ;   �      �  :   �  :   �  %     0   5  3   f  g   �  T     .   W  $   �  '   �     �  t   S     �  !   �  ,   �     '     E  "   [  O   ~  %   �     �  :   t  c   �     	     (	  -   >	     l	     y	     	     �	  	   �	     �	     �	     �	     �	  	   �	     �	     �	     
     
  8  
  N   R  F   �  2   �  4     3   P  g   �  T   �  .   A  $   p  .   �  �   �  t   R     �  !   �  *        0     L  /   a  T   �  5   �  �     :   �  c   �     L     _  =   t     �     �     �     �  	   �     �     �     �       	             .     L     U        #         
                                                     )                           %   &                     	               !                 $      (      "                              '    A human-friendly identifier to refer to this subscription. An upper limit in seconds to the exponential backoff time. Client ID to construct the auth token Comma-separated list of channels to subscribe to Datum en tijd waarop de actie heeft plaatsgevonden. De actie die door de publicerende API is gedaan. De publicerende API specificeert de toegestane acties. De naam van het kanaal (`KANAAL.naam`) waar het bericht op moet worden gepubliceerd. De resourcenaam waar de notificatie over gaat. Een waarde behorende bij de sleutel. Ensure this value is not in the future. If specified, a factor applied to the exponential backoff. This allows you to tune how quickly automatic retries are performed. Mapping van kenmerken (sleutel/waarde) van de notificatie. De publicerende API specificeert de toegestane kenmerken. NC subscription Notificatiescomponentconfiguratie Notifications API configuration ({api_root}) Notifications API integration Register the webhooks Secret to construct the auth token Something went wrong while registering subscription for {callback}: {exception} Subscription as it is known in the NC The maximum number of automatic retries. After this amount of retries, guaranteed delivery stops trying to deliver the message. URL-referentie naar de `resource` van de publicerende API. URL-referentie naar het hoofd object van de publicerende API die betrekking heeft op de `resource`. Webhook subscription Webhook subscriptions Where to send the notifications (webhook url) aanmaakdatum actie callback url channels client ID client secret hoofd object kanaal kenmerk kenmerken no service configured notifications api service resource resource URL Project-Id-Version: 0.3.1
Report-Msgid-Bugs-To: 
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
 Een voor mensen bedoelde kenmerkende naam om naar dit abonnement te verwijzen. Een bovenlimiet in seconden voor de maximale exponentiële vertraging. Client-ID om het autorisatietoken mee te genereren Kommagescheiden lijst van kanalen om op te abonneren Datum en tijd waarop de actie heeft plaatsgevonden. De actie die door de publicerende API is gedaan. De publicerende API specificeert de toegestane acties. De naam van het kanaal (`KANAAL.naam`) waar het bericht op moet worden gepubliceerd. De resourcenaam waar de notificatie over gaat. Een waarde behorende bij de sleutel. Zorg dat deze waarde niet in de toekomst ligt. Indien opgegeven wordt deze factor toegepast op de exponentiële vertraging. Dit laat toe om de frequentie van afleverpogingen in te stellen. Mapping van kenmerken (sleutel/waarde) van de notificatie. De publicerende API specificeert de toegestane kenmerken. Notificaties-API-abonnement Notificatiescomponentconfiguratie Notificaties-API-configuratie ({api_root}) Integratie Notificaties-API Webhooks registreren Secret om het autorisatietoken mee te genereren Er ging iets fout bij het registreren van een abonnement voor {callback}:{exception} Abonnement zoals die bekend is in de Notificaties-API De bovengrens voor het aantal automatische pogingen tot opnieuw verzenden. Na deze hoeveelheid pogingen stoppen de automatische afleverpogingen. URL-referentie naar de `resource` van de publicerende API. URL-referentie naar het hoofd object van de publicerende API die betrekking heeft op de `resource`. Webhook-abonnement Webhook-abonnementen Waar de notificaties gepubliceerd moeten worden (webhook-url) aanmaakdatum actie callback-url kanalen client-ID client-secret hoofdobject kanaal kenmerk kenmerken geen service ingesteld service voor notificaties-api resource resource-URL 